import yaml, re
from langdetect import detect
from flashtext import KeywordProcessor
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer

class DentalNLP:
    def __init__(self, kb_path="kb/dental_conditions.yaml"):
        with open(kb_path, encoding="utf-8") as f:
            self.kb = yaml.safe_load(f)["conditions"]

        self.keyword_processors = {}
        for lang in ("en", "hi", "bn"):
            kp = KeywordProcessor(case_sensitive=False)
            for cond in self.kb:
                syms = cond.get("symptoms", {}).get(lang, [])
                for s in syms:
                    kp.add_keyword(s, (cond["id"], s))
            self.keyword_processors[lang] = kp

        self.lang_docs = {"en": [], "hi": [], "bn": []}
        self.ids = []
        for cond in self.kb:
            self.ids.append(cond["id"])
            for lang in ("en", "hi", "bn"):
                text = " ".join(cond.get("symptoms", {}).get(lang, [])) + " " + cond.get("description", {}).get(lang, "")
                self.lang_docs[lang].append(text)

        self.vectorizers = {lang: TfidfVectorizer().fit(self.lang_docs[lang]) for lang in self.lang_docs}
        self.tfidf_matrix = {lang: self.vectorizers[lang].transform(self.lang_docs[lang]) for lang in self.lang_docs}

    def detect_lang(self, text):
        try:
            l = detect(text)
            if l.startswith("hi"): return "hi"
            if l.startswith("bn"): return "bn"
            return "en"
        except:
            return "en"

    def extract_symptoms(self, text, lang="en"):
        kp = self.keyword_processors.get(lang)
        matches = kp.extract_keywords(text)
        found = {}
        for cid, sym in matches:
            found.setdefault(cid, set()).add(sym)
        return found

    def fuzzy_score(self, text, lang="en"):
        scores = {}
        for i, cid in enumerate(self.ids):
            doc = self.lang_docs[lang][i]
            from rapidfuzz import fuzz
            s = fuzz.token_set_ratio(text, doc) / 100.0
            scores[cid] = s
        return scores

    def tfidf_similarity(self, text, lang="en"):
        vec = self.vectorizers[lang].transform([text])
        sims = (self.tfidf_matrix[lang] * vec.T).toarray().ravel()
        return dict(zip(self.ids, sims.tolist()))

    def rank(self, text):
        lang = self.detect_lang(text)
        symptoms_found = self.extract_symptoms(text, lang)
        tf = self.tfidf_similarity(text, lang)
        fuzzy = self.fuzzy_score(text, lang)

        results = []
        for cid in self.ids:
            match_count = len(symptoms_found.get(cid, []))
            score = 0.6 * tf.get(cid, 0) + 0.25 * fuzzy.get(cid, 0) + 0.15 * (match_count > 0)
            results.append((cid, score, match_count))

        results.sort(key=lambda x: x[1], reverse=True)
        best = results[0]  # only top-1

        cid, score, mc = best
        cond = next(c for c in self.kb if c["id"] == cid)
        top = {
            "id": cid,
            "score": score,
            "matched_symptoms": list(symptoms_found.get(cid, [])),
            "names": cond["names"],
            "advice": cond["advice"].get(lang),
            "specialist": cond["specialist"],
            "urgency": cond["urgency"]
        }
        return lang, top
