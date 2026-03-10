import sys
import os
import json
import base64
import re
import uuid
import traceback
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import rawpy
from PIL import Image
import requests
import exifread
import qtawesome as qta

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QListWidget, QProgressBar, QLineEdit, QLabel, 
                             QFileDialog, QDialog, QFormLayout, QSpinBox, QDoubleSpinBox,
                             QFrame, QListWidgetItem, QGraphicsDropShadowEffect, QComboBox,
                             QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QSize, QPoint
from PyQt6.QtGui import QColor, QPalette, QMouseEvent

# --- 日志配置 ---
logging.basicConfig(
    filename='process.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)

# --- 配置管理 ---
CONFIG_FILE = "config.json"
#TEMPLATE_FILE = "template.xmp"
XMP_TEMPLATE_CONTENT = """<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 7.0-c000">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/"
   crs:Version="18.0"
   crs:ProcessVersion="15.4"
   crs:RawFileName="{raw_filename}"
   crs:AlreadyApplied="False"
   crs:WhiteBalance="{WhiteBalance}"
   crs:Temperature="{Temperature}"
   crs:Tint="{Tint}"
   crs:Exposure2012="{Exposure}"
   crs:Contrast2012="{Contrast}"
   crs:Highlights2012="{Highlights}"
   crs:Shadows2012="{Shadows}"
   crs:Whites2012="{Whites}"
   crs:Blacks2012="{Blacks}"
   crs:Texture="{Texture}"
   crs:Clarity2012="{Clarity}"
   crs:Dehaze="{Dehaze}"
   crs:Vibrance="{Vibrance}"
   crs:Saturation="{Saturation}"
   crs:ParametricShadows="{ParametricShadows}"
   crs:ParametricDarks="{ParametricDarks}"
   crs:ParametricLights="{ParametricLights}"
   crs:ParametricHighlights="{ParametricHighlights}"
   crs:HueAdjustmentRed="{HueAdjustmentRed}"
   crs:HueAdjustmentOrange="{HueAdjustmentOrange}"
   crs:HueAdjustmentYellow="{HueAdjustmentYellow}"
   crs:HueAdjustmentGreen="{HueAdjustmentGreen}"
   crs:HueAdjustmentAqua="{HueAdjustmentAqua}"
   crs:HueAdjustmentBlue="{HueAdjustmentBlue}"
   crs:HueAdjustmentPurple="{HueAdjustmentPurple}"
   crs:HueAdjustmentMagenta="{HueAdjustmentMagenta}"
   crs:SaturationAdjustmentRed="{SaturationAdjustmentRed}"
   crs:SaturationAdjustmentOrange="{SaturationAdjustmentOrange}"
   crs:SaturationAdjustmentYellow="{SaturationAdjustmentYellow}"
   crs:SaturationAdjustmentGreen="{SaturationAdjustmentGreen}"
   crs:SaturationAdjustmentAqua="{SaturationAdjustmentAqua}"
   crs:SaturationAdjustmentBlue="{SaturationAdjustmentBlue}"
   crs:SaturationAdjustmentPurple="{SaturationAdjustmentPurple}"
   crs:SaturationAdjustmentMagenta="{SaturationAdjustmentMagenta}"
   crs:LuminanceAdjustmentRed="{LuminanceAdjustmentRed}"
   crs:LuminanceAdjustmentOrange="{LuminanceAdjustmentOrange}"
   crs:LuminanceAdjustmentYellow="{LuminanceAdjustmentYellow}"
   crs:LuminanceAdjustmentGreen="{LuminanceAdjustmentGreen}"
   crs:LuminanceAdjustmentAqua="{LuminanceAdjustmentAqua}"
   crs:LuminanceAdjustmentBlue="{LuminanceAdjustmentBlue}"
   crs:LuminanceAdjustmentPurple="{LuminanceAdjustmentPurple}"
   crs:LuminanceAdjustmentMagenta="{LuminanceAdjustmentMagenta}"
   crs:SplitToningShadowHue="{SplitToningShadowHue}"
   crs:SplitToningShadowSaturation="{SplitToningShadowSaturation}"
   crs:SplitToningHighlightHue="{SplitToningHighlightHue}"
   crs:SplitToningHighlightSaturation="{SplitToningHighlightSaturation}"
   crs:ToneCurveName2012="{ToneCurveName2012}"
   crs:Sharpness="{Sharpness}"
   crs:SharpenRadius="{SharpenRadius}"
   crs:SharpenDetail="{SharpenDetail}"
   crs:SharpenEdgeMasking="{SharpenEdgeMasking}"
   crs:LensProfileEnable="{LensProfileEnable}"
   crs:ChromaticAberrationLow="{ChromaticAberrationLow}"
   crs:PerspectiveVertical="{PerspectiveVertical}"
   crs:PerspectiveHorizontal="{PerspectiveHorizontal}"
   crs:PerspectiveRotate="{PerspectiveRotate}"
   crs:PerspectiveAspect="{PerspectiveAspect}"
   crs:PerspectiveScale="{PerspectiveScale}"
   crs:PerspectiveX="{PerspectiveX}"
   crs:PerspectiveY="{PerspectiveY}"
   crs:HasSettings="True">
   <crs:ToneCurvePV2012>
    <rdf:Seq>
     {ToneCurvePV2012}
    </rdf:Seq>
   </crs:ToneCurvePV2012>
   <crs:ToneCurvePV2012Red>
    <rdf:Seq>
     {ToneCurvePV2012Red}
    </rdf:Seq>
   </crs:ToneCurvePV2012Red>
   <crs:ToneCurvePV2012Green>
    <rdf:Seq>
     {ToneCurvePV2012Green}
    </rdf:Seq>
   </crs:ToneCurvePV2012Green>
   <crs:ToneCurvePV2012Blue>
    <rdf:Seq>
     {ToneCurvePV2012Blue}
    </rdf:Seq>
   </crs:ToneCurvePV2012Blue>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>"""

DEFAULT_MODEL_CONFIG = {
    "name": "Default GPT-4o",
    "base_url": "https://api.openai.com/v1",
    "api_key": "",
    "model": "gpt-4o",
    "temperature": 0.7,
    "max_tokens": 1500
}

DEFAULT_CONFIG = {
    "models": [DEFAULT_MODEL_CONFIG],
    "current_model_index": 0,
    "concurrency": 3,
    "jpeg_quality": 80
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "models" not in data:
                    old_model = {
                        "name": "Default",
                        "base_url": data.get("base_url", DEFAULT_MODEL_CONFIG["base_url"]),
                        "api_key": data.get("api_key", ""),
                        "model": data.get("model", "gpt-4o"),
                        "temperature": data.get("temperature", 0.7),
                        "max_tokens": data.get("max_tokens", 1500)
                    }
                    data = {
                        "models": [old_model], 
                        "current_model_index": 0, 
                        "concurrency": data.get("concurrency", 3),
                        "jpeg_quality": data.get("jpeg_quality", 80)
                    }
                if "jpeg_quality" not in data:
                    data["jpeg_quality"] = 80
                return data
        except:
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

# def get_xmp_template():
#     if not os.path.exists(TEMPLATE_FILE):
#         return "<x:xmpmeta>Error: template.xmp not found</x:xmpmeta>"
#     with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
#         return f.read()
def get_xmp_template():
    # 不再读文件，直接返回字符串
    return XMP_TEMPLATE_CONTENT
# --- 信号系统 ---
class WorkerSignals(QObject):
    finished = pyqtSignal(str, bool, dict) 
    progress = pyqtSignal(str, int) 

# --- 核心逻辑线程 ---
class ProcessTask:
    def __init__(self, raw_path, config, user_prompt, signals):
        self.raw_path = raw_path
        self.config = config
        self.model_config = config['models'][config['current_model_index']]
        self.user_prompt = user_prompt
        self.signals = signals
        self.filename = os.path.basename(raw_path)
        self.temp_jpg = None

    def run(self):
        attempts = 0
        success = False
        error_msg = ""
        
        log_info(f"开始处理文件: {self.filename}")
        
        while attempts < 2 and not success:
            try:
                self.signals.progress.emit(self.filename, 10)
                self.temp_jpg = os.path.join(os.path.dirname(self.raw_path), f"temp_{uuid.uuid4().hex}.jpg")
                
                with rawpy.imread(self.raw_path) as raw:
                    rgb = raw.postprocess(use_camera_wb=True, half_size=True, no_auto_bright=True, bright=1.0)
                    img = Image.fromarray(rgb)
                    img.thumbnail((1024, 1024))
                    # 修复：使用设置中的压缩率
                    img.save(self.temp_jpg, "JPEG", quality=self.config.get('jpeg_quality', 80))
                
                self.signals.progress.emit(self.filename, 30)
                exif_info = self.extract_exif()
                log_info(f"[{self.filename}] EXIF 提取成功")
                
                # 修复：AI 开始前增加进度提示
                self.signals.progress.emit(self.filename, 40)
                ai_params = self.call_ai(self.temp_jpg)
                log_info(f"[{self.filename}] AI 成功返回参数")
                
                self.signals.progress.emit(self.filename, 90)
                template = get_xmp_template()
                
                full_data = {
                    "raw_filename": self.filename,
                    "extension": os.path.splitext(self.filename)[1][1:].upper(),
                    "WhiteBalance": "As Shot", 
                    "Temperature": "", 
                    "Tint": "",
                    "Exposure": "+0.00", 
                    "Contrast": "0", 
                    "Highlights": "0", 
                    "Shadows": "0",
                    "Whites": "0", 
                    "Blacks": "0", 
                    "Texture": "0", 
                    "Clarity": "0", 
                    "Dehaze": "0", 
                    "Vibrance": "0", 
                    "Saturation": "0",
                    "HueAdjustmentRed": "0", "HueAdjustmentOrange": "0", "HueAdjustmentYellow": "0",
                    "HueAdjustmentGreen": "0", "HueAdjustmentAqua": "0", "HueAdjustmentBlue": "0",
                    "HueAdjustmentPurple": "0", "HueAdjustmentMagenta": "0",
                    "SaturationAdjustmentRed": "0", "SaturationAdjustmentOrange": "0", "SaturationAdjustmentYellow": "0",
                    "SaturationAdjustmentGreen": "0", "SaturationAdjustmentAqua": "0", "SaturationAdjustmentBlue": "0",
                    "SaturationAdjustmentPurple": "0", "SaturationAdjustmentMagenta": "0",
                    "LuminanceAdjustmentRed": "0", "LuminanceAdjustmentOrange": "0", "LuminanceAdjustmentYellow": "0",
                    "LuminanceAdjustmentGreen": "0", "LuminanceAdjustmentAqua": "0", "LuminanceAdjustmentBlue": "0",
                    "LuminanceAdjustmentPurple": "0", "LuminanceAdjustmentMagenta": "0",
                    "SplitToningShadowHue": "0", "SplitToningShadowSaturation": "0",
                    "SplitToningHighlightHue": "0", "SplitToningHighlightSaturation": "0",
                    "ParametricShadows": "0", "ParametricDarks": "0", "ParametricLights": "0", "ParametricHighlights": "0",
                    "ToneCurveName2012": "Linear",
                    "ToneCurvePV2012": "<rdf:li>0, 0</rdf:li><rdf:li>255, 255</rdf:li>",
                    "ToneCurvePV2012Red": "<rdf:li>0, 0</rdf:li><rdf:li>255, 255</rdf:li>",
                    "ToneCurvePV2012Green": "<rdf:li>0, 0</rdf:li><rdf:li>255, 255</rdf:li>",
                    "ToneCurvePV2012Blue": "<rdf:li>0, 0</rdf:li><rdf:li>255, 255</rdf:li>",
                    "Sharpness": "40", 
                    "SharpenRadius": "1.0", 
                    "SharpenDetail": "25", 
                    "SharpenEdgeMasking": "0",
                    "LensProfileEnable": "1", 
                    "ChromaticAberrationLow": "1",
                    "PerspectiveVertical": "0", 
                    "PerspectiveHorizontal": "0", 
                    "PerspectiveRotate": "0.0", 
                    "PerspectiveAspect": "0", 
                    "PerspectiveScale": "100", 
                    "PerspectiveX": "0.00", 
                    "PerspectiveY": "0.00"
                }
                # 修复：处理 AI 返回的曲线参数
                curve_keys = ["ToneCurvePV2012", "ToneCurvePV2012Red", "ToneCurvePV2012Green", "ToneCurvePV2012Blue"]
                for ck in curve_keys:
                    if ck in ai_params and isinstance(ai_params[ck], list):
                        points = ai_params[ck]
                        # 将 AI 返回的列表 ["0, 0", "255, 255"] 转换为 XMP 格式的字符串
                        ai_params[ck] = "".join([f"<rdf:li>{p}</rdf:li>" for p in points])
                        ai_params["ToneCurveName2012"] = "Custom"
                
                # 更新 AI 返回的所有参数到 full_data
                full_data.update(ai_params)
                # 修复：如果白平衡为 As Shot，且 AI 没给具体数值，从 XMP 标签中移除或填入默认占位符
                if full_data["WhiteBalance"] == "As Shot":
                    if not full_data["Temperature"]: full_data["Temperature"] = ""
                    if not full_data["Tint"]: full_data["Tint"] = ""                
                try:
                    xmp_content = template.format(**full_data)
                except KeyError as ke:
                    missing_key = str(ke)
                    log_error(f"[{self.filename}] 模板解析失败，缺少元数据: {missing_key}")
                    raise Exception(f"模板缺少键: {missing_key}")

                xmp_path = os.path.splitext(self.raw_path)[0] + ".xmp"
                with open(xmp_path, "w", encoding="utf-8") as f:
                    f.write(xmp_content)
                
                success = True
                log_info(f"[{self.filename}] 处理成功，XMP 已保存")
                self.signals.finished.emit(self.filename, True, {})
                self.signals.progress.emit(self.filename, 100)
                
            except Exception as e:
                attempts += 1
                error_msg = str(e)
                log_error(f"[{self.filename}] 第 {attempts} 次尝试失败: {error_msg}\n{traceback.format_exc()}")
                if attempts >= 2:
                    self.signals.finished.emit(self.filename, False, {"error": error_msg})
            finally:
                if self.temp_jpg and os.path.exists(self.temp_jpg):
                    try: os.remove(self.temp_jpg)
                    except: pass

    # 替换 extract_exif 函数
    def extract_exif(self):
        data = {
            "make": "Unknown", "model": "Unknown", 
            "date_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "exposure_time": "1/100", "f_number": "4.0", "iso": "100",
            "focal_length": "0", "focal_length_35mm": "0", "lens_model": "Unknown"
        }
        try:
            with open(self.raw_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
                def get_val(tag_name):
                    tag = tags.get(tag_name)
                    if not tag: return None
                    if hasattr(tag, 'values') and len(tag.values) > 0:
                        val = tag.values[0]
                        if hasattr(val, 'num') and hasattr(val, 'den'):
                            if val.den == 0: return "0"
                            if tag_name == 'EXIF ExposureTime': return f"{val.num}/{val.den}"
                            return str(round(float(val.num) / float(val.den), 1))
                    return str(tag)

                data["make"] = get_val('Image Make') or "Unknown"
                data["model"] = get_val('Image Model') or "Unknown"
                
                dt_raw = get_val('Image DateTime') or get_val('EXIF DateTimeOriginal')
                if dt_raw and len(dt_raw) >= 19:
                    data["date_time"] = dt_raw[:10].replace(':', '-') + "T" + dt_raw[11:19]
                
                data["exposure_time"] = get_val('EXIF ExposureTime') or "1/100"
                data["f_number"] = get_val('EXIF FNumber') or "4.0"
                data["iso"] = re.sub(r'[^\d]', '', get_val('EXIF ISOSpeedRatings') or "100")
                data["focal_length"] = get_val('EXIF FocalLength') or "0"
                data["focal_length_35mm"] = get_val('EXIF FocalLengthIn35mmFilm') or data["focal_length"]
                data["lens_model"] = get_val('EXIF LensModel') or "Unknown"
        except Exception as e:
            log_error(f"[{self.filename}] EXIF 提取异常: {str(e)}")
        return data
    

    def call_ai(self, image_path):
        with open(image_path, "rb") as f:
            b64_img = base64.b64encode(f.read()).decode('utf-8')
        
        # 修复：Prompt 增加对曲线和点曲线的要求
        step1_prompt = """Role
顶级数字影像后期专家 / 资深摄影后期顾问
你是一位精通 Adobe Camera Raw (ACR) 和 Lightroom 的后期专家。你拥有极高的审美水准，能通过视觉描述精准判断图片的优化空间，并提供从底层校准到顶层艺术化渲染的全套参数方案。

Workflow
请按照以下步骤对用户描述的图片进行深度分析并给出建议：

1. 影像诊断与风格定义
诊断分析： 识别当前图片的曝光分布、色彩倾向（直方图趋势）、构图优劣以及光影质感。
目标风格： 明确优化后的视觉目标（如：电影感、胶片感、高调商业、暗调极简等）。
2. ACR 全局参数调整（核心面板）
白平衡 (White Balance)： 给出具体的【色温】、【色调】调整方向。
基础色调 (Basic Tone)： 明确【曝光】、【对比度】、【高光】、【阴影】、【白色阶】、【黑色阶】的数值逻辑。
外观偏好 (Presence)： 包含【纹理】、【清晰度】、【去薄雾】、【鲜艳度】、【饱和度】。
3. 影调与曲线 (Tone Curve)
参数曲线： 调节阴影、深色调、浅色调、高光。
点曲线： 描述 R/G/B 通道及 RGB 复合曲线的具体走势（如：S型、拉高黑位等）。
务必对曲线进行调节，即使是十分微小的调节
4. 色彩精控 (HSL & Calibration)
颜色混合器 (HSL/Color Mixer)： 必须严格执行以下格式：
色相 (Hue)： 红[值]、橙[值]、黄[值]、绿[值]、浅蓝[值]、蓝[值]、紫[值]、洋红[值]
饱和度 (Saturation)： 红[值]...（以此类推）
明度 (Luminance)： 红[值]...（以此类推）
相机校准 (Calibration)： 调整【阴影色调】及红、绿、蓝三原色的【色相】与【饱和度】（用于底层肤色或通透度校正）。
5. 艺术化渲染 (Color Grading & Effects)
颜色分级 (Color Grading)： 详细给出【阴影】、【中间调】、【高光】的色相(H)、饱和度(S)、亮度(L)以及【平衡】与【混合】参数。
HDR 模式： 若涉及高动态场景，请说明 HDR 编辑模式下的参数补偿。
效果 (Effects)： 包含【颗粒】（大小/粗糙度）及【裁剪后暗角】。
6. 质量控制 (Detail & Corrections)
细节 (Detail)： 提供【锐化】（半径/细节/蒙版）与【降噪】（明度/色彩降噪）的具体数值。
镜头校正 (Lens Corrections)： 包含色差校正、配置文件校正、扭曲度及暗角补偿建议。
Output Constraints
口吻： 保持专业、严谨、富有艺术洞察力。
格式： 采用自然语言分析结合列表化参数，所有参数都需要有具体的值。
完整性： 必须涵盖上述所有模块，无需修改就输出该参数值为0或者其他默认值，不得遗漏任何一个提到的参数分类。
逻辑： 参数建议需符合逻辑（例如：提高对比度时需注意高光的压制）。
原图均为RAW图片，而你看到的时转换为的jpg图片，要考虑RAW转jpg和压缩带来的画质和色彩损失
如果未提出需要特殊风格，则以保持平衡为主"""

        headers = {"Authorization": f"Bearer {self.model_config['api_key']}", "Content-Type": "application/json"}
        
        payload_step1 = {
            "model": self.model_config['model'],
            "messages": [
                {"role": "system", "content": step1_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": f"用户风格需求：{self.user_prompt}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                ]}
            ],
            "temperature": self.model_config['temperature']
        }
        
        resp1 = requests.post(f"{self.model_config['base_url']}/chat/completions", headers=headers, json=payload_step1, timeout=90)
        resp1.raise_for_status()
        advice_text = resp1.json()['choices'][0]['message']['content']
        
        # 修复：JSON 转换 Prompt 增加曲线键名
        step2_prompt = """你是一个摄影后期数据转换引擎。你的任务是将专家的后期建议精确量化为 Adobe Camera Raw 标准的 XMP 参数。

### 输出规范：
1. **格式**：必须输出一个扁平化的 JSON 对象。
2. **数据类型**：所有值必须是字符串格式。
3. **参数范围**：
   - `Exposure`: 必须带正负号的浮点数，如 "+0.50", "-1.25", "+0.00"。
   - `Temperature`: 整数，范围 2000-50000（如 "5500"）。
   - `Tint`: 整数，范围 -150 到 +150。
   - `Contrast`, `Highlights`, `Shadows`, `Whites`, `Blacks`, `Texture`, `Clarity`, `Dehaze`, `Vibrance`, `Saturation`: 整数，范围 -100 到 +100。
   - `HSL色彩`: 包含 Hue(色相), Saturation(饱和度), Luminance(明度) 各8个颜色。范围 -100 到 +100。
   - `SplitToning`: Hue 范围 0-360，Saturation 范围 0-100。
4. **白平衡逻辑**：
   - 如果调整了色温(Temperature)或色调(Tint)，必须设置 "WhiteBalance": "Custom"。
   - 如果未调整，请务必设置 "WhiteBalance": "As Shot"，此时 Temperature 和 Tint 返回空字符串 ""。

### 必须包含的完整键名列表（严禁缺少，可以根据需要增加，但是要符合规范，比如曲线等信息）：
{
  "WhiteBalance": "Custom",
  "Temperature": "5200",
  "Tint": "0",
  "Exposure": "+0.00",
  "Contrast": "0",
  "Highlights": "0",
  "Shadows": "0",
  "Whites": "0",
  "Blacks": "0",
  "Texture": "0",
  "Clarity": "0",
  "Dehaze": "0",
  "Vibrance": "0",
  "Saturation": "0",
  "HueAdjustmentRed": "0", "HueAdjustmentOrange": "0", "HueAdjustmentYellow": "0", "HueAdjustmentGreen": "0", 
  "HueAdjustmentAqua": "0", "HueAdjustmentBlue": "0", "HueAdjustmentPurple": "0", "HueAdjustmentMagenta": "0",
  "SaturationAdjustmentRed": "0", "SaturationAdjustmentOrange": "0", "SaturationAdjustmentYellow": "0", "SaturationAdjustmentGreen": "0", 
  "SaturationAdjustmentAqua": "0", "SaturationAdjustmentBlue": "0", "SaturationAdjustmentPurple": "0", "SaturationAdjustmentMagenta": "0",
  "LuminanceAdjustmentRed": "0", "LuminanceAdjustmentOrange": "0", "LuminanceAdjustmentYellow": "0", "LuminanceAdjustmentGreen": "0", 
  "LuminanceAdjustmentAqua": "0", "LuminanceAdjustmentBlue": "0", "LuminanceAdjustmentPurple": "0", "LuminanceAdjustmentMagenta": "0",
  "SplitToningShadowHue": "0", "SplitToningShadowSaturation": "0",
  "SplitToningHighlightHue": "0", "SplitToningHighlightSaturation": "0",
  "ToneCurveName2012": "Custom",
  "ToneCurvePV2012": ["0, 0", "64, 50", "128, 128", "192, 200", "255, 255"]
  "ToneCurvePV2012Red": ["0, 0", "255, 255"],
  "ToneCurvePV2012Green": ["0, 0", "255, 255"],
  "ToneCurvePV2012Blue": ["0, 0", "255, 255"],
  "Sharpness": "40",
  "SharpenRadius": "1.0",
  "SharpenDetail": "25",
  "SharpenEdgeMasking": "0",
  "LensProfileEnable": "1",
  "ChromaticAberrationLow": "1",
  "PerspectiveVertical": "0",
  "PerspectiveHorizontal": "0",
  "PerspectiveRotate": "0.0",
  "PerspectiveAspect": "0",
  "PerspectiveScale": "100",
  "PerspectiveX": "0.00",
  "PerspectiveY": "0.00"
}
注意：坐标点必须是 "输入, 输出" 格式字符串，范围 0-255。如果某通道不需要调整，请务必提供默认的 ["0, 0", "255, 255"]。
请根据专家的分析建议，给出结构化的json文件。如果建议中未提及某项，请设为 "0"（Exposure设为 "+0.00"，Temperature设为 "5000"）。"""
        payload_step2 = {
            "model": self.model_config['model'],
            "messages": [
                {"role": "system", "content": step2_prompt},
                {"role": "user", "content": f"请将以下建议转换为JSON格式：\n{advice_text}"}
            ],
            "response_format": {"type": "json_object"}
        }

        resp2 = requests.post(f"{self.model_config['base_url']}/chat/completions", headers=headers, json=payload_step2, timeout=60)
        resp2.raise_for_status()
        return json.loads(resp2.json()['choices'][0]['message']['content'])

# --- UI 组件 ---

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumWidth(500)
        self.config = load_config()
        self.init_ui()
        self._drag_pos = QPoint()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame { background-color: #f0f4f8; border-radius: 20px; border: 1px solid #dce4ec; }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox { background-color: white; color: #333; border: 1px solid #ddd; border-radius: 8px; padding: 8px; }
            QLabel { color: #333; font-weight: bold; background: transparent; border:none;}
            QPushButton { padding: 8px 15px; border-radius: 8px; font-weight: bold;}
            QPushButton#SaveBtn { background-color: #4a90e2; color: white; border: none; }
            QPushButton#AddBtn { background-color: #2ecc71; color: white; border: none; }
            QPushButton#DelBtn { background-color: #e74c3c; color: white; border: none; }
            QPushButton#CloseBtnSmall { background-color: #ff5f57; border-radius: 7px; border: none; }
        """)
        
        container_layout = QVBoxLayout(self.container)
        
        title_bar = QHBoxLayout()
        title_lbl = QLabel("模型与系统参数设置")
        title_lbl.setStyleSheet("font-size: 14px;")
        btn_close = QPushButton()
        btn_close.setObjectName("CloseBtnSmall")
        btn_close.setFixedSize(14, 14)
        btn_close.clicked.connect(self.reject)
        title_bar.addWidget(title_lbl)
        title_bar.addStretch()
        title_bar.addWidget(btn_close)
        container_layout.addLayout(title_bar)

        top_h = QHBoxLayout()
        self.model_selector = QComboBox()
        self.refresh_model_list()
        self.model_selector.currentIndexChanged.connect(self.load_selected_model)
        
        btn_add = QPushButton("新增")
        btn_add.setObjectName("AddBtn")
        btn_add.clicked.connect(self.add_new_model)
        
        btn_del = QPushButton("删除")
        btn_del.setObjectName("DelBtn")
        btn_del.clicked.connect(self.delete_model)
        
        top_h.addWidget(self.model_selector, 1)
        top_h.addWidget(btn_add)
        top_h.addWidget(btn_del)
        container_layout.addLayout(top_h)

        self.form = QFormLayout()
        self.name_edit = QLineEdit()
        self.url_edit = QLineEdit()
        self.key_edit = QLineEdit()
        self.key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.model_name_edit = QLineEdit()
        self.temp_spin = QDoubleSpinBox(); self.temp_spin.setRange(0, 2); self.temp_spin.setSingleStep(0.1)
        self.token_spin = QSpinBox(); self.token_spin.setRange(100, 80000); self.token_spin.setSingleStep(100)
        
        self.form.addRow("配置名称:", self.name_edit)
        self.form.addRow("Base URL:", self.url_edit)
        self.form.addRow("API Key:", self.key_edit)
        self.form.addRow("模型标识:", self.model_name_edit)
        self.form.addRow("Temperature:", self.temp_spin)
        self.form.addRow("Max Tokens:", self.token_spin)
        
        container_layout.addLayout(self.form)
        
        # 修复：增加压缩率设置和并发设置
        sys_form = QFormLayout()
        self.conc_spin = QSpinBox(); self.conc_spin.setRange(1, 10); self.conc_spin.setValue(self.config.get('concurrency', 3))
        self.quality_spin = QSpinBox(); self.quality_spin.setRange(10, 100); self.quality_spin.setValue(self.config.get('jpeg_quality', 80))
        sys_form.addRow("全局并发任务数:", self.conc_spin)
        sys_form.addRow("JPG预览压缩质量(10-100):", self.quality_spin)
        container_layout.addLayout(sys_form)

        btn_save = QPushButton("保存并应用")
        btn_save.setObjectName("SaveBtn")
        btn_save.clicked.connect(self.save_all)
        container_layout.addWidget(btn_save)

        self.main_layout.addWidget(self.container)
        self.load_selected_model(self.config['current_model_index'])

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def refresh_model_list(self):
        self.model_selector.blockSignals(True)
        self.model_selector.clear()
        for m in self.config['models']:
            self.model_selector.addItem(m['name'])
        self.model_selector.setCurrentIndex(self.config['current_model_index'])
        self.model_selector.blockSignals(False)

    def load_selected_model(self, index):
        if index < 0 or index >= len(self.config['models']): return
        m = self.config['models'][index]
        self.name_edit.setText(m['name'])
        self.url_edit.setText(m['base_url'])
        self.key_edit.setText(m['api_key'])
        self.model_name_edit.setText(m['model'])
        self.temp_spin.setValue(m['temperature'])
        self.token_spin.setValue(m['max_tokens'])

    def add_new_model(self):
        new_m = DEFAULT_MODEL_CONFIG.copy()
        new_m['name'] = f"新模型 {len(self.config['models'])+1}"
        self.config['models'].append(new_m)
        self.config['current_model_index'] = len(self.config['models']) - 1
        self.refresh_model_list()
        self.load_selected_model(self.config['current_model_index'])

    def delete_model(self):
        if len(self.config['models']) <= 1:
            QMessageBox.warning(self, "提示", "至少需要保留一个模型配置。")
            return
        idx = self.model_selector.currentIndex()
        self.config['models'].pop(idx)
        self.config['current_model_index'] = 0
        self.refresh_model_list()
        self.load_selected_model(0)

    def save_all(self):
        idx = self.model_selector.currentIndex()
        self.config['models'][idx] = {
            "name": self.name_edit.text(),
            "base_url": self.url_edit.text(),
            "api_key": self.key_edit.text(),
            "model": self.model_name_edit.text(),
            "temperature": self.temp_spin.value(),
            "max_tokens": self.token_spin.value()
        }
        self.config['current_model_index'] = idx
        self.config['concurrency'] = self.conc_spin.value()
        self.config['jpeg_quality'] = self.quality_spin.value()
        save_config(self.config)
        self.accept()

class FileWidget(QWidget):
    def __init__(self, filename):
        super().__init__()
        layout = QHBoxLayout(self)
        self.label = QLabel(filename)
        self.label.setStyleSheet("font-weight: bold; color: #333; background: transparent;")
        self.status = QLabel("待处理")
        self.status.setStyleSheet("color: #777; font-size: 11px; background: transparent;")
        self.pbar = QProgressBar()
        self.pbar.setFixedHeight(6)
        self.pbar.setTextVisible(False)
        self.pbar.setStyleSheet("QProgressBar { background: #eee; border-radius: 3px; } QProgressBar::chunk { background: #a2c2e8; border-radius: 3px; }")
        self.retry_btn = QPushButton(qta.icon('fa5s.sync-alt', color='#666'), "")
        self.retry_btn.setFixedSize(24, 24)
        self.retry_btn.setVisible(False)
        self.retry_btn.setStyleSheet("border: none; background: transparent;")

        vbox = QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addWidget(self.status)
        layout.addLayout(vbox, 1)
        layout.addWidget(self.pbar, 1)
        layout.addWidget(self.retry_btn)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.raw_files = []
        self.item_widgets = {}
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setFixedSize(1000, 720)
        self.init_ui()
        self._drag_pos = QPoint()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget#CentralWidget { background: transparent; }
            QFrame#MainContainer { background-color: #f0f4f8; border-radius: 25px; }
            QFrame#LeftPanel { background-color: rgba(255, 255, 255, 0.5); border-radius: 20px; margin: 10px; }
            QPushButton#ActionBtn { background-color: white; border: 1px solid #dce4ec; border-radius: 12px; padding: 10px; font-weight: bold; color: #5a6b7d; text-align: left; }
            QPushButton#ActionBtn:hover { background-color: #eef2f6; }
            QPushButton#CloseBtn { background-color: #ff5f57; border-radius: 8px; border: none; }
            QPushButton#MinBtn { background-color: #febc2e; border-radius: 8px; border: none; }
            QPushButton#MaxBtn { background-color: #28c840; border-radius: 8px; border: none; }
            QLineEdit { border-radius: 10px; padding: 12px; border: 1px solid #d0d7de; background: white; color: #333; }
            QComboBox { border-radius: 8px; padding: 5px 10px; border: 1px solid #d0d7de; background: white; color: #333; }
            QListWidget { border: none; background: white; border-radius: 15px; padding: 5px; }
            QLabel#Title { font-size: 18px; font-weight: bold; color: #2c3e50; background: transparent;}
        """)

        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        
        outer_layout = QVBoxLayout(central_widget)
        outer_layout.setContentsMargins(15, 15, 15, 15)

        self.container = QFrame()
        self.container.setObjectName("MainContainer")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30); shadow.setXOffset(0); shadow.setYOffset(10)
        shadow.setColor(QColor(0,0,0,40))
        self.container.setGraphicsEffect(shadow)
        
        main_layout = QVBoxLayout(self.container)
        
        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(25, 15, 20, 0)
        title_label = QLabel("AI xmp Generator")
        title_label.setObjectName("Title")
        
        self.btn_min = QPushButton()
        self.btn_min.setFixedSize(16, 16)
        self.btn_min.setObjectName("MinBtn")
        self.btn_min.clicked.connect(self.showMinimized)

        self.btn_max = QPushButton()
        self.btn_max.setFixedSize(16, 16)
        self.btn_max.setObjectName("MaxBtn")
        self.btn_max.clicked.connect(self.toggle_max_restore)

        btn_close = QPushButton()
        btn_close.setFixedSize(16, 16)
        btn_close.setObjectName("CloseBtn")
        btn_close.clicked.connect(self.close)
        
        title_bar.addWidget(title_label)
        title_bar.addStretch()
        title_bar.addWidget(self.btn_min)
        title_bar.addSpacing(5)
        title_bar.addWidget(self.btn_max)
        title_bar.addSpacing(5)
        title_bar.addWidget(btn_close)
        main_layout.addLayout(title_bar)

        content_layout = QHBoxLayout()
        
        left_panel_frame = QFrame()
        left_panel_frame.setObjectName("LeftPanel")
        left_panel = QVBoxLayout(left_panel_frame)
        left_panel.setContentsMargins(20, 20, 20, 20)
        
        left_panel.addWidget(QLabel("<b>工作模型选择</b>"))
        self.model_dropdown = QComboBox()
        self.update_model_dropdown()
        self.model_dropdown.currentIndexChanged.connect(self.change_active_model)
        left_panel.addWidget(self.model_dropdown)
        left_panel.addSpacing(15)

        left_panel.addWidget(QLabel("<b>调色风格描述</b>"))
        self.user_req = QLineEdit()
        self.user_req.setPlaceholderText("例如：复古电影、明亮清新...")
        left_panel.addWidget(self.user_req)
        
        tip = QLabel("AI 将基于图像内容与指令生成 XMP 调色元数据。")
        tip.setWordWrap(True)
        tip.setStyleSheet("color: #7f8c8d; font-size: 11px; margin-top: 5px; background:transparent;")
        left_panel.addWidget(tip)
        
        left_panel.addStretch()
        
        self.btn_import = QPushButton(qta.icon('fa5s.plus-circle', color='#4a90e2'), " 导入图片/文件夹")
        self.btn_import.setObjectName("ActionBtn")
        self.btn_start = QPushButton(qta.icon('fa5s.magic', color='#2ecc71'), " 开始批量处理")
        self.btn_start.setObjectName("ActionBtn")
        self.btn_settings = QPushButton(qta.icon('fa5s.cog', color='#7f8c8d'), " 设置与系统参数")
        self.btn_settings.setObjectName("ActionBtn")
        self.btn_clear = QPushButton(qta.icon('fa5s.trash-alt', color='#e74c3c'), " 清空任务列表")
        self.btn_clear.setObjectName("ActionBtn")
        
        for b in [self.btn_import, self.btn_start, self.btn_settings, self.btn_clear]:
            left_panel.addWidget(b)
        
        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(10, 10, 10, 10)
        
        header = QHBoxLayout()
        self.lbl_count = QLabel("待处理: 0")
        self.lbl_done = QLabel("已完成: 0")
        self.lbl_count.setStyleSheet("color: #34495e; font-weight: bold; background:transparent;")
        self.lbl_done.setStyleSheet("color: #27ae60; font-weight: bold; background:transparent;")
        header.addWidget(self.lbl_count); header.addStretch(); header.addWidget(self.lbl_done)
        right_panel.addLayout(header)
        
        self.list_widget = QListWidget()
        right_panel.addWidget(self.list_widget)

        content_layout.addWidget(left_panel_frame, 1)
        content_layout.addLayout(right_panel, 2)
        main_layout.addLayout(content_layout)
        outer_layout.addWidget(self.container)

        self.btn_import.clicked.connect(self.import_files_dialog)
        self.btn_settings.clicked.connect(self.open_settings)
        self.btn_start.clicked.connect(self.process_all)
        self.btn_clear.clicked.connect(self.clear_list)

    def toggle_max_restore(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def update_model_dropdown(self):
        self.model_dropdown.blockSignals(True)
        self.model_dropdown.clear()
        for m in self.config['models']:
            self.model_dropdown.addItem(qta.icon('fa5s.cube', color='#4a90e2'), m['name'])
        self.model_dropdown.setCurrentIndex(self.config['current_model_index'])
        self.model_dropdown.blockSignals(False)

    def change_active_model(self, index):
        self.config['current_model_index'] = index
        save_config(self.config)

    def import_files_dialog(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("导入资源")
        msg.setText("请选择导入方式：")
        btn_files = msg.addButton("选择独立图片", QMessageBox.ButtonRole.ActionRole)
        btn_dir = msg.addButton("选择整个文件夹", QMessageBox.ButtonRole.ActionRole)
        msg.addButton("取消", QMessageBox.ButtonRole.RejectRole)
        msg.exec()
        
        selected_files = []
        exts = ('.NEF', '.DNG', '.ARW', '.CR2', '.CR3', '.ORF', '.RAF', '.GPR')
        
        if msg.clickedButton() == btn_files:
            files, _ = QFileDialog.getOpenFileNames(self, "选择一张或多张图片", "", f"RAW Files ({' '.join(['*'+e for e in exts])})")
            selected_files = files
        elif msg.clickedButton() == btn_dir:
            dir_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
            if dir_path:
                selected_files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.upper().endswith(exts)]
        
        for f in selected_files:
            if f not in self.raw_files:
                self.raw_files.append(f)
                self.add_list_item(f)
        self.lbl_count.setText(f"待处理: {len(self.raw_files)}")

    def add_list_item(self, file_path):
        fname = os.path.basename(file_path)
        item = QListWidgetItem(self.list_widget)
        item.setSizeHint(QSize(0, 70))
        widget = FileWidget(fname)
        self.list_widget.setItemWidget(item, widget)
        self.item_widgets[fname] = (widget, file_path)
        widget.retry_btn.clicked.connect(lambda: self.process_single(fname))

    def clear_list(self):
        self.list_widget.clear()
        self.raw_files = []
        self.item_widgets = {}
        self.lbl_count.setText("待处理: 0")
        self.lbl_done.setText("已完成: 0")

    def open_settings(self):
        if SettingsDialog(self).exec():
            self.config = load_config()
            self.update_model_dropdown()

    def process_all(self):
        cur_m = self.config['models'][self.config['current_model_index']]
        if not cur_m['api_key']:
            QMessageBox.warning(self, "配置缺失", "当前模型未配置 API Key。")
            return
        
        # if not os.path.exists(TEMPLATE_FILE):
        #     QMessageBox.critical(self, "错误", "未找到 template.xmp 模板文件！")
        #     return

        executor = ThreadPoolExecutor(max_workers=self.config.get('concurrency', 3))
        for fname in list(self.item_widgets.keys()):
            executor.submit(self.process_single, fname)

    def process_single(self, fname):
        widget, full_path = self.item_widgets[fname]
        widget.retry_btn.setVisible(False)
        widget.status.setText("准备中...")
        
        signals = WorkerSignals()
        signals.progress.connect(self.update_progress)
        signals.finished.connect(self.on_task_finished)
        
        task = ProcessTask(full_path, self.config, self.user_req.text(), signals)
        task.run()

    def update_progress(self, fname, val):
        if fname in self.item_widgets:
            self.item_widgets[fname][0].pbar.setValue(val)
            self.item_widgets[fname][0].status.setText(f"处理中 {val}%")

    def on_task_finished(self, fname, success, data):
        widget = self.item_widgets[fname][0]
        if success:
            widget.status.setText("✅ 已生成 XMP")
            widget.status.setStyleSheet("color: #2ecc71; font-weight: bold; background:transparent;")
            try:
                current_text = self.lbl_done.text()
                done_val = int(re.search(r'\d+', current_text).group())
                self.lbl_done.setText(f"已完成: {done_val + 1}")
            except: pass
        else:
            error_msg = data.get('error', '未知')
            display_error = (error_msg[:30] + '..') if len(error_msg) > 30 else error_msg
            widget.status.setText(f"❌ 失败: {display_error}")
            widget.status.setStyleSheet("color: #e74c3c; font-size: 10px; background:transparent;")
            widget.retry_btn.setVisible(True)

if __name__ == "__main__":
    if os.path.exists('process.log'):
        try: os.remove('process.log')
        except: pass

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(qta.icon('fa5s.camera-retro', color='#4a90e2'))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())