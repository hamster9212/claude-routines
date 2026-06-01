%% MATLAB 4대 함수 씹어먹기 — 학생 실습 문제 모범 답안
% 강사용 | 배포 전 파일명 변경 권장

%% ========================================================
%  문제 1 정답
% =========================================================
fprintf('=== 문제 1 정답 ===\n');

scores = [78, 92, 65, 88, 95, 71, 83, 59, 100, 76];

[top_score, top_idx] = max(scores);
fprintf('최고: %d점 (학생 %d번)\n', top_score, top_idx);

low_score = min(scores);
fprintf('최저: %d점\n', low_score);

score_range = max(scores) - min(scores);
fprintf('범위: %d점\n\n', score_range);

% 채점 포인트:
%   - max() 사용 (min() 사용 시 오답)
%   - [m,i] = max() 형식으로 인덱스까지 추출
%   - 범위: max - min

%% ========================================================
%  문제 2 정답
% =========================================================
fprintf('=== 문제 2 정답 ===\n');

sales = [120, 135, NaN, 142, 118;
          98, NaN, 103,  NaN, 115;
         205, 198, 212, 195, NaN];
branch   = {'지점1','지점2','지점3'};
day_name = {'월','화','수','목','금'};

for b = 1:3
    [peak_sales, day_idx] = max(sales(b,:), 'omitnan');
    fprintf('%s 최대: %d개 (%s요일)\n', branch{b}, peak_sales, day_name{day_idx});
end

overall_min = min(sales(:), 'omitnan');
fprintf('전체 최솟값 (NaN 제외): %d\n\n', overall_min);

% 채점 포인트:
%   - max(sales(b,:), 'omitnan') — omitnan 빠지면 NaN 반환
%   - sales(:)로 펼쳐서 전체 스칼라 추출
%   - min(sales, [], 'all', 'omitnan')도 허용 (R2020a+)

%% ========================================================
%  문제 3 정답
% =========================================================
fprintf('=== 문제 3 정답 ===\n');

f = @(x) exp(x) - 3*x;

figure('Name', '문제3: e^x - 3x = 0');
fplot(f, [0, 3], 'b-', 'LineWidth', 2);
hold on; yline(0, 'r--'); grid on;
title('e^x - 3x = 0'); xlabel('x'); ylabel('f(x)');

[x1, fv1, flag1] = fzero(f, [0, 1]);
[x2, fv2, flag2] = fzero(f, [1, 2]);

plot(x1, 0, 'ro', 'MarkerSize', 12, 'MarkerFaceColor', 'r');
plot(x2, 0, 'go', 'MarkerSize', 12, 'MarkerFaceColor', 'g');

fprintf('근 1: x = %.6f  (f=%.2e, flag=%d)\n', x1, fv1, flag1);
fprintf('근 2: x = %.6f  (f=%.2e, flag=%d)\n\n', x2, fv2, flag2);

% 채점 포인트:
%   - 그래프를 먼저 그려 구간 파악 (필수 습관)
%   - 구간 [a,b] 사용 (단일 x0 사용해도 허용, 단 불안정)
%   - exitflag 확인 및 출력
%   - 근 2개 모두 탐색

%% ========================================================
%  문제 4 정답
% =========================================================
fprintf('=== 문제 4 정답 ===\n');

x_data = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0];
y_data = [0.3, 1.8, 2.1, 1.2, -0.5, -1.9, -2.0];

sin_model = @(v, x) v(1) * sin(v(2)*x + v(3));
obj = @(v) sum((y_data - sin_model(v, x_data)).^2);

options = optimset('TolFun', 1e-10, 'TolX', 1e-10, 'MaxIter', 5000, 'Display', 'off');
[p_opt, rss, flag] = fminsearch(obj, [2, 2, 0], options);

fprintf('a=%.4f, b=%.4f, c=%.4f\n', p_opt(1), p_opt(2), p_opt(3));
fprintf('RSS=%.6f, flag=%d\n\n', rss, flag);

figure('Name', '문제4: sin 모델 피팅');
x_fine = linspace(0, 3, 200);
plot(x_data, y_data, 'ro', 'MarkerSize', 10, 'LineWidth', 2);
hold on;
plot(x_fine, sin_model(p_opt, x_fine), 'b-', 'LineWidth', 2);
xlabel('x'); ylabel('y');
title(sprintf('sin 피팅: y=%.3f·sin(%.3f·x+%.3f)', p_opt));
legend('데이터', '피팅 결과'); grid on;

% 채점 포인트:
%   - @(v, x) 형식 모델 함수 (또는 @(v) 내에서 x_data 직접 참조)
%   - v(1), v(2), v(3)으로 파라미터 접근
%   - RSS 목적 함수 올바르게 작성
%   - 그래프 시각화

%% ========================================================
%  보너스 정답
% =========================================================
fprintf('=== 보너스 정답: Himmelblau 4개 최솟값 ===\n');

himmel = @(v) (v(1)^2 + v(2) - 11)^2 + (v(1) + v(2)^2 - 7)^2;
opts = optimset('TolFun', 1e-10, 'TolX', 1e-10, 'Display', 'off');

% 4개 최솟값 근방의 초기값
init_pts = [0,0; -1,3; -3,-3; 4,-2];

fprintf('초기값 → 수렴점:\n');
for i = 1:4
    [xi, fi] = fminsearch(himmel, init_pts(i,:), opts);
    fprintf('(%2.0f,%2.0f) → (%.4f, %.4f)  f=%.2e\n', ...
        init_pts(i,1), init_pts(i,2), xi(1), xi(2), fi);
end

% 채점 포인트:
%   - 초기값이 각기 다른 골짜기에 있어야 함
%   - for 루프로 반복 fminsearch 실행
%   - 4개 모두 f ≈ 0 (1e-8 이하) 달성

fprintf('\n=== 모든 문제 완료 ===\n');
