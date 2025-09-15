class turkish_str(str):  # noqa
    CHARMAP = {
        "to_upper": {
            "ı": "I",
            "i": "İ",
        },
        "to_lower": {
            "I": "ı",
            "İ": "i",
        },
    }

    def lower(self):
        for key, value in self.CHARMAP.get("to_lower").items():
            self = self.replace(key, value)

        return self.lower()

    def upper(self):
        for key, value in self.CHARMAP.get("to_upper").items():
            self = self.replace(key, value)

        return self.upper()

    def capitalize(self):
        first, rest = self[0], self[1:]
        return turkish_str(first).upper() + turkish_str(rest).lower()

    def title(self):
        return " ".join(map(lambda x: turkish_str(x).capitalize(), self.split()))
