def calculate_grade(average):
    """평균 점수를 바탕으로 학점을 계산하는 함수입니다."""
    if average >= 90: return 'A'
    elif average >= 80: return 'B'
    elif average >= 70: return 'C'
    elif average >= 60: return 'D'
    else: return 'F'

def main():
    print("🎓 성적 계산 프로그램을 시작합니다!")
    
    # 1. 인원수 입력받기
    try:
        num_people = int(input("입력할 인원수를 입력하세요: "))
    except ValueError:
        print("숫자만 입력해주세요. 프로그램을 종료합니다.")
        return

    students = []
    overall_total = 0

    print(f"\n💡 {num_people}명의 '이름 국어 영어 컴퓨터' 점수를 띄어쓰기로 구분해서 한 줄에 입력해주세요.")
    print("예시: 홍길동 90 85 95\n")

    # 2. 학생 정보 입력 및 개인별 계산
    for i in range(num_people):
        while True:
            try:
                user_input = input(f"[{i+1}/{num_people}] 학생 정보 입력: ")
                # 공백을 기준으로 문자열을 나눕니다.
                name, kor, eng, com = user_input.split()
                kor, eng, com = int(kor), int(eng), int(com)
                
                # 총점, 평균, 학점 계산
                total = kor + eng + com
                avg = total / 3
                grade = calculate_grade(avg)
                
                # 딕셔너리 형태로 학생 정보 저장
                students.append({
                    'name': name, 'kor': kor, 'eng': eng, 'com': com,
                    'total': total, 'avg': avg, 'grade': grade
                })
                
                # 전체 총점 누적
                overall_total += total
                break # 성공적으로 입력받으면 while 루프를 탈출하여 다음 학생으로 넘어감
                
            except ValueError:
                print("입력 형식이 잘못되었습니다. 다시 입력해주세요. (예: 홍길동 90 85 95)")

    # 3. 전체 성적 계산
    if num_people > 0:
        overall_avg = overall_total / (num_people * 3) # 전체 과목 수로 나눔
        overall_grade = calculate_grade(overall_avg)
    else:
        overall_avg = 0
        overall_grade = 'F'

    # 4. 결과 출력하기
    print("\n" + "=" * 55)
    print("개인별 성적 결과")
    print("=" * 55)
    print(f"{'이름':<5} | {'국어':<3} | {'영어':<3} | {'컴퓨터':<3} | {'총점':<4} | {'평균':<5} | {'학점':<3}")
    print("-" * 55)
    
    for s in students:
        # :<5는 5칸을 확보하고 왼쪽 정렬, :.1f는 소수점 첫째 자리까지 표시하라는 의미입니다.
        print(f"{s['name']:<5} | {s['kor']:<4} | {s['eng']:<4} | {s['com']:<6} | {s['total']:<4} | {s['avg']:<5.1f} | {s['grade']:<3}")
    
    print("=" * 55)
    print("전체 성적 결과")
    print("=" * 55)
    print(f"전체 총점: {overall_total}")
    print(f"전체 평균: {overall_avg:.1f}")
    print(f"전체 학점: {overall_grade}")

if __name__ == "__main__":
    main()