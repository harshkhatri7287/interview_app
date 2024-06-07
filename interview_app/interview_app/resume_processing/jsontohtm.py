import json
import re

title = ""


class HTMLWriter:

    def __init__(self):
        self.resume_content = ''

    def process_tag(self, el):
        print(f"processing element at path {el['Path']}")
        tag = re.sub(r'\[\d+\]', '', el['Path'].split('/')[-1])
        style = ""
        styles = []
        global title
        if "Aside" in el.get("Path", ""):
            return None
        if "Kids" in el.keys():
            return HTMLWriter.process_kids(self, el.get("Kids"))

        if el.get("Font"):
            if "family_name" in el["Font"]:
                styles.append(f"font-family: {el['Font']['family_name']}, sans-serif;")
        if el.get("TextSize"):
            if "TextSize" in el:
                styles.append(f"font-size: {el['TextSize']}px;")
        if el.get("attributes"):
            if "attributes" in el and "LineHeight" in el["attributes"]:
                styles.append(f"line-height: {el['attributes']['LineHeight']}px;")
            if "attributes" in el and "SpaceAfter" in el["attributes"]:
                styles.append(f"margin-bottom: {el['attributes']['SpaceAfter']}px;")
        if styles:
            style += f' style="{" ".join(styles)}"'
        if tag == 'Title':
            title += f'<head><title {style}> {el.get("Text", "")} </title></head>'
            return f'<h1 {style}> {el.get("Text", "")} </h1>'
        if tag == 'H1':
            return f'<h1 {style}> {el.get("Text", "")} </h1>'
        if tag == 'H2':
            return f'<h2 {style}> {el.get("Text", "")} </h2>'
        if tag == 'H3':
            return f'<h3 {style}> {el.get("Text", "")} </h3>'
        if tag == 'P' or tag == 'LBody':
            if 'Table' not in el.get("Path"):
                print(el.get("Path"))
                self.resume_content += f'\n{el.get("Text", "")}'
                return f'<p {style}> {el.get("Text", "")}</p>'
        if tag == 'Figure':
            if el.get("filePaths"):
                bounds = el.get("Bounds", "")
                object_id = el.get("electID", "")
                bbox = el.get("attributes", "").get("BBox", "")

                left, top, right, bottom = bounds
                img_left, img_top, img_right, img_bottom = bbox

                width = right - left
                height = bottom - top
                img_width = img_right - img_left
                img_height = img_bottom - img_top
                filepath = el.get("filePaths", [""])[0]
                return f"""<figure id="figure-{object_id}">
        <img src="{filepath}" alt="" width="{img_width}" height="{img_height}" style="position: relative; left: {img_left - left}px; top: {img_top - top}px; width: {img_width}px; height: {img_height}px;" />
        </figure>"""

    def process_kids(self, arr):
        para = "<p>"
        complete_text = ""
        styles = []
        style = ""
        for i in arr:
            if i.get("Text"):
                font = i['Font']
                if font:
                    if font['family_name']:
                        font_familiy = f"font-family: {font['family_name']}, sans-serif;"
                        if font_familiy not in styles:
                            styles.append(font_familiy)
                    if font['weight']:
                        font_weight = f"font-weight: {font['weight']}, sans-serif;"
                        if font_weight not in styles:
                            styles.append(font_weight)
                    if i.get("TextSize"):
                        text_size = f"font-size: {i['TextSize']}px;"
                        if text_size not in styles:
                            styles.append(text_size)
                    if i.get("attributes"):
                        if "attributes" in i and "LineHeight" in i["attributes"]:
                            line_height = f"line-height: {i['attributes']['LineHeight']}px;"
                            if line_height not in styles:
                                styles.append(line_height)
                        if "attributes" in i and "SpaceAfter" in i["attributes"]:
                            space_after = f"margin-bottom: {i['attributes']['SpaceAfter']}px;"
                            if space_after not in styles:
                                styles.append(space_after)

                    if i.get("Font"):
                        if i.get("Font").get("italic"):
                            complete_text += f"<em> {i.get('Text')} </em>"
                        else:
                            complete_text += i['Text']

        if styles:
            style += f' style="{" ".join(styles)}"'
            para = f"<p {style}>"
        para += complete_text
        self.resume_content += complete_text
        para += "</p>"
        return para

    def htmlwriter(self, structuredDataJson):
        file_name = "".join(structuredDataJson.split(".")[0].split('/')[0])
        file_name = "/home/beehyv/Desktop" if file_name == '' else file_name
        input_json = structuredDataJson
        jf = open(input_json, encoding="utf8")
        data = json.load(jf)

        paths = []
        for i in data['elements']:
            paths.append(re.sub(r'\[\d+\]', '', i['Path'].split('/')[-1]))

        h1t = []
        for i in data['elements']:
            res = HTMLWriter.process_tag(self, i)
            h1t.append(res)

        return self.resume_content