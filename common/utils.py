# common/utils.py

import markdown2

def md2(content, tag='psm-md2'):
    return f"<div class='{tag}'>" + markdown2.markdown(content, extras=["cuddled-lists", "break-on-newline", "tables"]) + "</div><!--md2-->"