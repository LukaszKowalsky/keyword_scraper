from flask import Flask

app = Flask(__name__)
app.secret_key = "2/gV[l7APKo^muZ3L!2*_%o0B8~Vt:l"

import keyword_scraper.views
