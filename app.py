import os
import time
import hashlib
import psutil
from datetime import datetime
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# Счётчики для метрик
visit_count = 0
prediction_requests_count = 0
start_time = time.time()

# Пул чисто астрологических предсказаний
PREDICTIONS_POOL = [
    "Сегодня звезды сулят неожиданную встречу, которая может приятно удивить.",
    "Благоприятный день для финансовых начинаний и планирования крупных покупок.",
    "Энергия дня подталкивает к творчеству. Смело беритесь за новые хобби и идеи.",
    "Возможны приятные сюрпризы в личной жизни. Будьте открыты к общению.",
    "Отличный момент для отдыха и перезагрузки. Посвятите вечер тому, что приносит радость.",
    "Интуиция сегодня будет на высоте. Доверяйте своему внутреннему голосу при принятии решений.",
    "Звезды советуют уделить внимание гармонии: отправьтесь на прогулку или отдохните в тишине.",
    "Ваша харизма сегодня привлечет нужных людей. Пользуйтесь моментом для знакомств.",
    "День наполнен легкой энергетикой. Все дела будут решаться быстрее и проще, чем обычно.",
    "Не бойтесь менять планы на ходу: спонтанность принесет самые яркие эмоции.",
    "Луна шепчет, что пора отпустить старые тревоги и освободить место для хороших новостей.",
    "Ожидайте вестей издалека. Они поднимут вам настроение на долгое время.",
    "Прекрасное время для планирования путешествия или поездки мечты.",
    "Ваши старания и упорство наконец-то принесут долгожданные плоды.",
    "Звезды обещают уютный вечер в кругу близких и теплую атмосферу дома."
]

HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔮 Астрологический Портал</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: #090d16;
            color: #f8fafc;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px 20px;
            overflow-y: auto; 
            position: relative;
        }

        .bg-glow-1 {
            position: fixed;
            width: 450px;
            height: 450px;
            background: radial-gradient(circle, rgba(168, 85, 247, 0.25) 0%, rgba(0,0,0,0) 70%);
            top: -50px;
            left: -50px;
            border-radius: 50%;
            animation: pulse 8s ease-in-out infinite alternate;
            z-index: 1;
            pointer-events: none;
        }
        .bg-glow-2 {
            position: fixed;
            width: 500px;
            height: 500px;
            background: radial-gradient(circle, rgba(56, 189, 248, 0.18) 0%, rgba(0,0,0,0) 70%);
            bottom: -100px;
            right: -100px;
            border-radius: 50%;
            animation: pulse 10s ease-in-out infinite alternate;
            z-index: 1;
            pointer-events: none;
        }

        @keyframes pulse {
            0% { transform: scale(1) translate(0, 0); }
            100% { transform: scale(1.2) translate(30px, -30px); }
        }

        .star {
            position: fixed;
            background: #ffffff;
            border-radius: 50%;
            animation: twinkle var(--duration) ease-in-out infinite;
            z-index: 1;
            pointer-events: none;
        }

        @keyframes twinkle {
            0%, 100% { opacity: 0.2; transform: scale(0.8); }
            50% { opacity: 0.9; transform: scale(1.2); }
        }

        .container {
            max-width: 460px;
            width: 100%;
            z-index: 10;
            margin: auto;
        }

        .card {
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 28px;
            padding: 40px 30px;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.6);
            text-align: center;
        }

        .icon-header {
            font-size: 52px;
            margin-bottom: 12px;
            display: inline-block;
            filter: drop-shadow(0 0 15px rgba(192, 132, 252, 0.6));
        }

        h1 {
            color: #ffffff;
            font-size: 28px;
            margin-bottom: 6px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }

        .subtitle {
            color: #94a3b8;
            font-size: 14px;
            margin-bottom: 32px;
        }

        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-size: 12px;
            font-weight: 600;
            color: #a7f3d0;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        select, input[type="date"] {
            width: 100%;
            padding: 14px 16px;
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.12);
            background: rgba(9, 13, 22, 0.8);
            color: #fff;
            font-size: 15px;
            outline: none;
            transition: all 0.3s ease;
        }

        select:focus, input[type="date"]:focus {
            border-color: #c084fc;
            box-shadow: 0 0 0 4px rgba(192, 132, 252, 0.2);
        }

        button {
            background: linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%);
            color: white;
            border: none;
            padding: 16px;
            font-size: 16px;
            border-radius: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 10px;
            font-weight: 600;
            box-shadow: 0 10px 25px -5px rgba(217, 70, 239, 0.4);
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 30px -5px rgba(217, 70, 239, 0.6);
            filter: brightness(1.1);
        }

        #result {
            margin-top: 25px;
            padding: 22px;
            border-radius: 16px;
            background: rgba(9, 13, 22, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.08);
            min-height: 90px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .prediction-text {
            color: #fde047;
            font-size: 15px;
            line-height: 1.6;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="bg-glow-1"></div>
    <div class="bg-glow-2"></div>

    <script>
        for (let i = 0; i < 35; i++) {
            const star = document.createElement('div');
            star.className = 'star';
            star.style.top = Math.random() * 100 + 'vh';
            star.style.left = Math.random() * 100 + 'vw';
            const size = Math.random() * 2.5 + 1;
            star.style.width = size + 'px';
            star.style.height = size + 'px';
            star.style.setProperty('--duration', (Math.random() * 4 + 2) + 's');
            document.body.appendChild(star);
        }
    </script>

    <div class="container">
        <div class="card">
            <div class="icon-header">✨</div>
            <h1>Астролог Онлайн</h1>
            <p class="subtitle">Персональный гороскоп от звезд</p>

            <div class="form-group">
                <label for="zodiac">Знак зодиака</label>
                <select id="zodiac">
                    <option value="Овен">♈ Овен</option>
                    <option value="Телец">♉ Телец</option>
                    <option value="Близнецы">♊ Близнецы</option>
                    <option value="Рак">♋ Рак</option>
                    <option value="Лев">♌ Лев</option>
                    <option value="Дева">♍ Дева</option>
                    <option value="Весы">♎ Весы</option>
                    <option value="Скорпион">♏ Скорпион</option>
                    <option value="Стрелец">♐ Стрелец</option>
                    <option value="Козерог">♑ Козерог</option>
                    <option value="Водолей">♒ Водолей</option>
                    <option value="Рыбы">♓ Рыбы</option>
                </select>
            </div>

            <div class="form-group">
                <label for="date">Дата прогноза</label>
                <input type="date" id="date">
            </div>

            <button onclick="getPrediction()">Получить гороскоп</button>

            <div id="result">
                <span class="prediction-text" id="predictionText" style="color: #64748b;">Выберите знак и дату ✨</span>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); text-align: left;">
                <div style="font-size: 11px; font-weight: 600; color: #a7f3d0; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">📊 Мониторинг системы</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 13px; color: #94a3b8;">
                    <div style="background: rgba(9,13,22,0.6); padding: 10px; border-radius: 10px;">
                        Статус: <span id="mStatus" style="color: #2ee59d; font-weight: bold;">Загрузка...</span>
                    </div>
                    <div style="background: rgba(9,13,22,0.6); padding: 10px; border-radius: 10px;">
                        Посещений: <span id="mVisits" style="color: #fde047; font-weight: bold;">0</span>
                    </div>
                    <div style="background: rgba(9,13,22,0.6); padding: 10px; border-radius: 10px;">
                        CPU: <span id="mCpu" style="color: #38bdf8; font-weight: bold;">0%</span>
                    </div>
                    <div style="background: rgba(9,13,22,0.6); padding: 10px; border-radius: 10px;">
                        RAM: <span id="mRam" style="color: #c084fc; font-weight: bold;">0%</span>
                    </div>
                </div>
                <div style="margin-top: 10px; text-align: center;">
                    <a href="/metrics" target="_blank" style="font-size: 11px; color: #38bdf8; text-decoration: none;">🔗 Сырой JSON /metrics</a>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('date').valueAsDate = new Date();

        async function getPrediction() {
            const zodiac = document.getElementById('zodiac').value;
            const date = document.getElementById('date').value;
            const textElement = document.getElementById('predictionText');

            if (!date) {
                textElement.style.color = "#f87171";
                textElement.innerText = "Пожалуйста, выберите дату!";
                return;
            }

            textElement.style.color = "#cbd5e1";
            textElement.innerText = "Консультируемся со звездами...";

            try {
                const response = await fetch(`/api/predict?zodiac=${encodeURIComponent(zodiac)}&date=${date}`);
                const data = await response.json();
                textElement.style.color = "#fde047";
                textElement.innerText = `✨ ${zodiac} (${data.date}):\n${data.prediction}`;
            } catch (err) {
                textElement.style.color = "#f87171";
                textElement.innerText = "Не удалось получить предсказание.";
            }
        }
        
                async function fetchMetrics() {
            try {
                const res = await fetch('/metrics');
                const data = await res.json();
                document.getElementById('mStatus').innerText = data.app_metrics.status;
                document.getElementById('mVisits').innerText = data.app_metrics.total_page_visits;
                document.getElementById('mCpu').innerText = data.system_resources.cpu_usage_percent + '%';
                document.getElementById('mRam').innerText = data.system_resources.ram_usage_percent + '%';
            } catch (e) {
                console.error("Ошибка загрузки метрик");
            }
        }

        fetchMetrics();
        setInterval(fetchMetrics, 3000);
        
    </script>
</body>
</html>
"""


@app.route('/')
def home():
    global visit_count
    visit_count += 1
    return render_template_string(HOME_TEMPLATE)


@app.route('/api/predict')
def predict():
    global prediction_requests_count
    prediction_requests_count += 1

    zodiac = request.args.get('zodiac', 'Овен')
    date_str = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))

    seed_string = f"{zodiac}_{date_str}"
    hash_value = int(hashlib.md5(seed_string.encode('utf-8')).hexdigest(), 16)
    prediction_index = hash_value % len(PREDICTIONS_POOL)

    return jsonify({
        "zodiac": zodiac,
        "date": date_str,
        "prediction": PREDICTIONS_POOL[prediction_index]
    })


@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "uptime_seconds": int(time.time() - start_time)
    }), 200


@app.route('/metrics')
def metrics():
    cpu_usage = psutil.cpu_percent(interval=None)
    ram_usage = psutil.virtual_memory().percent

    return jsonify({
        "app_metrics": {
            "total_page_visits": visit_count,
            "total_predictions_generated": prediction_requests_count,
            "status": "running"
        },
        "system_resources": {
            "cpu_usage_percent": cpu_usage,
            "ram_usage_percent": ram_usage
        },
        "uptime_seconds": int(time.time() - start_time)
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)