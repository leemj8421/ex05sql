from flask import Flask, request, render_template_string

# Flask 웹 애플리케이션 생성
app = Flask(__name__)

# 화면에 보여줄 HTML 디자인 (파이썬 코드 안에 포함시켰습니다)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>파이썬 웹 성적 계산기</title>
    <style>
        body { font-family: 'Malgun Gothic', sans-serif; max-width: 800px; margin: 30px auto; padding: 20px; }
        textarea { width: 100%; padding: 10px; font-size: 14px; border: 1px solid #ccc; border-radius: 5px; }
        button { margin-top: 10px; padding: 10px 20px; background-color: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; text-align: center; }
        th, td { border: 1px solid #ddd; padding: 10px; }
        th { background-color: #f4f4f4; }
        .summary { margin-top: 20px; padding: 15px; background-color: #e9ecef; border-radius: 5px; }
        .error { color: red; font-weight: bold; margin-top: 10px; }
    </style>
</head>
<body>
    <h2>🎓 파이썬 웹 성적 계산 프로그램 (Flask)</h2>
    
    <form method="POST">
        <label><b>학생 정보 입력</b> (한 줄에 한 명씩 '이름 국어 영어 컴퓨터' 띄어쓰기로 입력하세요)</label><br><br>
        <textarea name="student_data" rows="8" placeholder="예시:&#10;홍길동 90 85 95&#10;김철수 70 80 75"></textarea><br>
        <button type="submit">성적 계산하기</button>
    </form>

    {% if error %}
        <div class="error">⚠️ {{ error }}</div>
    {% endif %}

    {% if results %}
        <h3>📊 개인별 성적 결과</h3>
        <table>
            <tr><th>이름</th><th>국어</th><th>영어</th><th>컴퓨터</th><th>총점</th><th>평균</th><th>학점</th></tr>
            {% for r in results %}
            <tr>
                <td>{{ r.name }}</td><td>{{ r.kor }}</td><td>{{ r.eng }}</td><td>{{ r.com }}</td>
                <td><b>{{ r.total }}</b></td><td>{{ "%.1f"|format(r.avg) }}</td><td><b>{{ r.grade }}</b></td>
            </tr>
            {% endfor %}
        </table>

        <div class="summary">
            <h3>🏆 전체 성적 결과</h3>
            <p><b>전체 총점:</b> {{ o_total }} 점</p>
            <p><b>전체 평균:</b> {{ "%.1f"|format(o_avg) }} 점</p>
            <p><b>전체 학점:</b> {{ o_grade }}</p>
        </div>
    {% endif %}
</body>
</html>
"""

def calculate_grade(average):
    """평균 점수를 바탕으로 학점을 계산합니다."""
    if average >= 90: return 'A'
    elif average >= 80: return 'B'
    elif average >= 70: return 'C'
    elif average >= 60: return 'D'
    else: return 'F'

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    overall_total = 0
    overall_avg = 0
    overall_grade = 'F'
    error = None

    # 사용자가 '계산하기' 버튼을 눌렀을 때 (POST 요청)
    if request.method == 'POST':
        # 텍스트 영역에 입력된 데이터 가져오기
        data = request.form.get('student_data', '')
        lines = data.strip().split('\n')
        
        try:
            for line in lines:
                if not line.strip(): continue # 빈 줄은 무시
                
                parts = line.split()
                if len(parts) != 4:
                    raise ValueError(f"'{line}'의 입력 형식이 맞지 않습니다.")
                
                name = parts[0]
                kor, eng, com = int(parts[1]), int(parts[2]), int(parts[3])
                
                # 계산 로직
                total = kor + eng + com
                avg = total / 3
                grade = calculate_grade(avg)
                
                results.append({
                    'name': name, 'kor': kor, 'eng': eng, 'com': com,
                    'total': total, 'avg': avg, 'grade': grade
                })
                overall_total += total
            
            # 전체 통계 계산
            if results:
                overall_avg = overall_total / (len(results) * 3)
                overall_grade = calculate_grade(overall_avg)
                
        except ValueError as e:
            error = f"입력 오류: {e} (숫자만 입력했는지, 띄어쓰기를 잘 했는지 확인해주세요.)"
            results = [] # 에러 발생 시 결과 초기화

    # HTML 템플릿과 파이썬 변수들을 연결하여 화면에 렌더링
    return render_template_string(
        HTML_TEMPLATE, 
        results=results, 
        o_total=overall_total, 
        o_avg=overall_avg, 
        o_grade=overall_grade, 
        error=error
    )

if __name__ == '__main__':
    # 웹 서버 실행 (디버그 모드를 켜서 에러 확인이 쉽게 합니다)
    app.run(debug=True)