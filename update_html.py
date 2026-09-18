import re

html_path = "vehicle-count-output/index.html"
with open(html_path, "r") as f:
    content = f.read()

new_buttons = """    <div class="cam-selector">
        <button class="cam-btn active" onclick="switchCamera('cvc3_cam_1', 'CVC 3 Cam 1', 'cvc3_cam_1.jpg', this)">📷 CVC 3 Cam 1</button>
        <button class="cam-btn" onclick="switchCamera('cvc4_cam_1', 'CVC 4 Cam 1', 'cvc4_cam_1.jpg', this)">📷 CVC 4 Cam 1</button>
        <button class="cam-btn" onclick="switchCamera('cvc5_cam_1__ir', 'CVC 5 Cam 1 IR', 'cvc5_cam_1__ir.jpg', this)">📷 CVC 5 Cam 1 IR</button>
        <button class="cam-btn" onclick="switchCamera('cvc5_cam_2', 'CVC 5 Cam 2', 'cvc5_cam_2.jpg', this)">📷 CVC 5 Cam 2</button>
        <button class="cam-btn" onclick="switchCamera('cvc6_cam_1__nb', 'CVC 6 Cam 1 NB', 'cvc6_cam_1__nb.jpg', this)">📷 CVC 6 Cam 1 NB</button>
        <button class="cam-btn" onclick="switchCamera('cvc6_cam_2__sb', 'CVC 6 Cam 2 SB', 'cvc6_cam_2__sb.jpg', this)">📷 CVC 6 Cam 2 SB</button>
        <button class="cam-btn" onclick="switchCamera('cvc7_cam_1__eb', 'CVC 7 Cam 1 EB', 'cvc7_cam_1__eb.jpg', this)">📷 CVC 7 Cam 1 EB</button>
        <button class="cam-btn" onclick="switchCamera('cvc7_cam_2__wb', 'CVC 7 Cam 2 WB', 'cvc7_cam_2__wb.jpg', this)">📷 CVC 7 Cam 2 WB</button>
        <button class="cam-btn" onclick="switchCamera('cvc8_cam_1', 'CVC 8 Cam 1', 'cvc8_cam_1.jpg', this)">📷 CVC 8 Cam 1</button>
        <button class="cam-btn" onclick="switchCamera('cvc9_cam_1', 'CVC 9 Cam 1', 'cvc9_cam_1.jpg', this)">📷 CVC 9 Cam 1</button>
        <button class="cam-btn" onclick="switchCamera('cvc10_cam_1', 'CVC 10 Cam 1', 'cvc10_cam_1.jpg', this)">�� CVC 10 Cam 1</button>
    </div>"""

pattern = re.compile(r'<div class="cam-selector">.*?</div>', re.DOTALL)
new_content = pattern.sub(new_buttons, content)

with open(html_path, "w") as f:
    f.write(new_content)
print("Done")
