%% MATLAB 4대 함수 씹어먹기 — 학생 실습 문제 (빈칸형)
% 이름: ________________________  날짜: ________________
% 각 문제를 완성하고 실행하여 결과를 확인하세요.

%% ========================================================
%  문제 1 (난이도: ★☆☆) — min / max 기본
% =========================================================
% 아래 점수 배열에서:
% 1. 최고 점수와 그 학생 번호(인덱스)를 출력하라
% 2. 최저 점수를 출력하라
% 3. 점수 범위(최고 - 최저)를 계산하라

scores = [78, 92, 65, 88, 95, 71, 83, 59, 100, 76];

% 1. 최고 점수와 학생 번호
[top_score, top_idx] = _____(scores);
fprintf('최고: %d점 (학생 %d번)\n', top_score, top_idx);

% 2. 최저 점수
low_score = _____(scores);
fprintf('최저: %d점\n', low_score);

% 3. 점수 범위
score_range = _____(scores) - _____(scores);
fprintf('범위: %d점\n', score_range);

%% ========================================================
%  문제 2 (난이도: ★★☆) — 행렬 방향 + NaN 처리
% =========================================================
% 3개 지점 × 5일 판매량 (NaN = 휴점)
% 1. 각 지점별 최대 판매량과 발생 요일을 출력하라
% 2. 전체에서 NaN을 제외한 절대 최솟값을 구하라

sales = [120, 135, NaN, 142, 118;
          98, NaN, 103,  NaN, 115;
         205, 198, 212, 195, NaN];
branch   = {'지점1','지점2','지점3'};
day_name = {'월','화','수','목','금'};

% 1. 지점별 최대 판매량 (행 방향, NaN 무시)
for b = 1:3
    [peak_sales, day_idx] = _____(sales(b,:), _____ );
    fprintf('%s 최대: %d개 (%s요일)\n', branch{b}, peak_sales, day_name{day_idx});
end

% 2. 전체 최솟값 (NaN 제외)
%    힌트: sales(:)로 펼친 후 omitnan 적용
overall_min = _____(_____, _____);
fprintf('전체 최솟값 (NaN 제외): %d\n', overall_min);

%% ========================================================
%  문제 3 (난이도: ★★☆) — fzero 근 탐색
% =========================================================
% e^x - 3x = 0 의 양의 실수 근을 모두 구하시오.
% 단계 1: 그래프를 그려 근의 개수와 위치를 확인하라
% 단계 2: 각 근에 대해 구간 [a,b]를 설정하여 fzero로 찾아라
% 단계 3: exitflag를 출력하여 수렴 성공 여부를 확인하라

f = @(x) _____(x) - 3*x;

% 단계 1: 그래프
figure;
fplot(f, [0, 3], 'b-', 'LineWidth', 2);
hold on; yline(0, 'r--'); grid on;
title('e^x - 3x = 0'); xlabel('x'); ylabel('f(x)');

% 단계 2: fzero 탐색
[x1, fv1, flag1] = fzero(f, [_____, _____]);   % 첫 번째 구간
[x2, fv2, flag2] = fzero(f, [_____, _____]);   % 두 번째 구간

% 단계 3: 결과 출력
fprintf('근 1: x = %.6f  (f=%.2e, flag=%d)\n', x1, fv1, flag1);
fprintf('근 2: x = %.6f  (f=%.2e, flag=%d)\n', x2, fv2, flag2);

%% ========================================================
%  문제 4 (난이도: ★★★) — fminsearch 커브피팅
% =========================================================
% y = a·sin(b·x + c) 모델로 아래 데이터를 피팅하시오.
% 초기값: [2, 2, 0]

x_data = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0];
y_data = [0.3, 1.8, 2.1, 1.2, -0.5, -1.9, -2.0];

% 모델 함수: v(1)=a, v(2)=b, v(3)=c
sin_model = @(v, x) _____(1) * sin( _____(2)*x + _____(3) );

% 목적 함수: 잔차제곱합 최소화
obj = @(v) sum( ( y_data - sin_model(v, x_data) ).^2 );

% fminsearch 실행
[p_opt, rss, flag] = fminsearch(obj, [2, 2, 0]);

% 결과 출력
fprintf('a=%.4f, b=%.4f, c=%.4f\n', p_opt(1), p_opt(2), p_opt(3));
fprintf('RSS=%.6f, flag=%d\n', rss, flag);

% 시각화
x_fine = linspace(0, 3, 200);
figure;
plot(x_data, y_data, 'ro', 'MarkerSize', 10, 'LineWidth', 2);
hold on;
plot(x_fine, sin_model(p_opt, x_fine), 'b-', 'LineWidth', 2);
xlabel('x'); ylabel('y');
title(sprintf('sin 모델 피팅: y=%.3f·sin(%.3f·x+%.3f)', p_opt));
legend('데이터', '피팅 결과'); grid on;

%% ========================================================
%  보너스 (난이도: ★★★) — fminsearch 다중 최솟값 탐색
% =========================================================
% Himmelblau 함수의 4개 최솟값을 모두 찾으시오.
% f(x,y) = (x^2+y-11)^2 + (x+y^2-7)^2
% 서로 다른 초기값에서 fminsearch를 4번 실행하라.

himmel = @(v) (v(1)^2 + v(2) - 11)^2 + (v(1) + v(2)^2 - 7)^2;

init_pts = [0,0; _____; _____; _____];   % 나머지 3개 초기값 채우기
opts = optimset('TolFun', 1e-10, 'TolX', 1e-10, 'Display', 'off');

fprintf('초기값 → 수렴점:\n');
for i = 1:4
    [xi, fi] = fminsearch(himmel, init_pts(i,:), opts);
    fprintf('(%.0f,%.0f) → (%.3f, %.3f)  f=%.2e\n', ...
        init_pts(i,1), init_pts(i,2), xi(1), xi(2), fi);
end
