from flask import Flask, render_template, request, jsonify
import requests
import time
import base64

app = Flask(__name__)

IMGBB_API_KEY = "ضع_مفتاح_API_من_imgbb"  # سجل مجاناً من imgbb.com

# --- دالة تعديل الصور ---
def edit_img_multiple(url1, prompt, num_images=1):
    results = []
    for _ in range(num_images):
        res = requests.post(
            "https://a1d.ai/api/nano-banana/edit",
            json={
                "prompt": str(prompt),
                "images": [url1],
                "enable_base64_output": False
            }
        ).json()

        task_id = res["data"]["id"]
        output_url = None
        for i in range(20):
            res1 = requests.get(f"https://a1d.ai/api/nano-banana/status?id={task_id}").json()
            if "outputs" in res1["data"] and len(res1["data"]["outputs"]) > 0:
                output_url = res1["data"]["outputs"][0]
                break
            time.sleep(5)

        if output_url:
            results.append(output_url)
    return results


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["image"]
    if not file:
        return jsonify({"error": "لم يتم رفع صورة"}), 400

    # تحويل الصورة base64 ورفعها على imgbb
    img_b64 = base64.b64encode(file.read())
    res = requests.post(
        "https://api.imgbb.com/1/upload",
        data={
            "key": IMGBB_API_KEY,
            "image": img_b64
        }
    ).json()

    if "data" in res:
        return jsonify({"url": res["data"]["url"]})
    else:
        return jsonify({"error": "فشل رفع الصورة"}), 500


@app.route("/process", methods=["POST"])
def process():
    data = request.json
    image_url = data.get("image_url")
    prompt_input = data.get("prompt")
    num_images = int(data.get("num_images", 1))

    # إضافة تعليمات للحفاظ على ملامح الوجه
    prompt = f"{prompt_input}. Keep all facial features, expressions, and identity exactly the same."

    result_urls = edit_img_multiple(image_url, prompt, num_images)
    return jsonify({"results": result_urls})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
  
