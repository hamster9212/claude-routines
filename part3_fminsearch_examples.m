%% MATLAB 4대 함수 씹어먹기 — 파트 3: fminsearch
% 강의 실습 스크립트 | 실행: F5 또는 섹션별 Ctrl+Enter

%% ========================================================
%  섹션 0: fzero vs fminsearch 차이 시각화
% =========================================================
fprintf('=== fzero vs fminsearch 차이 ===\n');

f_demo = @(x) (x-2).^2 + 1;   % 최솟값: x=2, f=1

figure('Name', 'fzero vs fminsearch');
x_range = -1:0.01:5;
plot(x_range, f_demo(x_range), 'b-', 'LineWidth', 2);
hold on; yline(0, 'r--', 'LineWidth', 1);
plot(2, 1, 'g^', 'MarkerSize', 14, 'MarkerFaceColor', 'g');
xlabel('x'); ylabel('f(x)');
title('fzero는 x축 교차점, fminsearch는 골짜기 바닥');
legend('f(x)', 'f(x)=0 기준선', '최솟점 (fminsearch 목표)');
grid on;
fprintf('(x-2)^2+1 의 최솟값: x=2 에서 f=1\n');
fprintf('이 함수는 x축을 통과하지 않으므로 fzero 사용 불가!\n\n');

[x_min, f_min] = fminsearch(f_demo, 0);
fprintf('fminsearch 결과: x=%.6f, f=%.6f\n\n', x_min, f_min);

%% ========================================================
%  예시 1: 커브피팅 — 지수 모델 파라미터 추정
% =========================================================
fprintf('=== 예시 1: 커브피팅 (y = a·exp(b·x)) ===\n');

x_data = [10, 20, 30, 40, 50, 60, 70, 80];
y_data = [2.1, 3.8, 7.2, 13.5, 25.1, 46.8, 88.2, 163.0];

model  = @(p, x) p(1) * exp(p(2) * x);
obj_fn = @(p) sum((y_data - model(p, x_data)).^2);

params0 = [1, 0.05];
options = optimset('TolFun', 1e-10, 'TolX', 1e-10, 'MaxIter', 5000, 'Display', 'off');
[p_opt, rss, flag] = fminsearch(obj_fn, params0, options);

fprintf('초기 RSS: %.4f\n', obj_fn(params0));
fprintf('최적 a = %.4f,  b = %.6f\n', p_opt(1), p_opt(2));
fprintf('최종 RSS = %.6f,  flag = %d\n\n', rss, flag);

figure('Name', '예시 1: 커브피팅');
x_fit = linspace(10, 80, 200);
plot(x_data, y_data, 'ro', 'MarkerSize', 10, 'LineWidth', 2);
hold on;
plot(x_fit, model(p_opt, x_fit), 'b-', 'LineWidth', 2);
plot(x_fit, model(params0, x_fit), 'g--', 'LineWidth', 1.5);
xlabel('온도 (°C)'); ylabel('반응 속도');
title(sprintf('커브피팅: y = %.4f·exp(%.5f·x)', p_opt(1), p_opt(2)));
legend('측정 데이터', '최적 피팅', '초기값 모델'); grid on;

%% ========================================================
%  예시 2: 물류 창고 최적 입지
% =========================================================
fprintf('=== 예시 2: 물류 창고 최적 입지 ===\n');

stores  = [10, 40; 60, 20; 35, 70];   % 매장 위치 (km)
weights = [3, 5, 2];                   % 물량 가중치

cost = @(pos) sum(weights .* sqrt((stores(:,1)' - pos(1)).^2 + ...
                                   (stores(:,2)' - pos(2)).^2));

x0 = [mean(stores(:,1)), mean(stores(:,2))];
fprintf('초기값 (중심): (%.1f, %.1f) km,  초기 비용: %.4f km\n', ...
    x0(1), x0(2), cost(x0));

options = optimset('TolFun', 1e-8, 'TolX', 1e-8, 'Display', 'off');
[pos_opt, cost_opt, flag] = fminsearch(cost, x0, options);

fprintf('최적 위치: (%.2f, %.2f) km\n', pos_opt(1), pos_opt(2));
fprintf('최소 비용: %.4f km  (개선: %.4f km)\n', cost_opt, cost(x0)-cost_opt);
fprintf('flag = %d\n\n', flag);

figure('Name', '예시 2: 물류 최적화');
store_names = {'매장A (w=3)', '매장B (w=5)', '매장C (w=2)'};
scatter(stores(:,1), stores(:,2), 200, 'bs', 'filled'); hold on;
scatter(pos_opt(1), pos_opt(2), 300, 'r^', 'filled');
scatter(x0(1), x0(2), 200, 'g^');
for i = 1:3
    plot([pos_opt(1), stores(i,1)], [pos_opt(2), stores(i,2)], 'r--', 'LineWidth', 1.5);
    text(stores(i,1)+1.5, stores(i,2)+1.5, store_names{i}, 'FontSize', 11);
end
xlabel('x (km)'); ylabel('y (km)');
title('물류 창고 최적 입지 선정');
legend('매장', '최적 창고', '초기 추정(중심)'); grid on; axis equal;

%% ========================================================
%  예시 3: 비볼록 함수 — 지역 최솟값 함정 (Himmelblau)
% =========================================================
fprintf('=== 예시 3: 지역 최솟값 함정 (Himmelblau 함수) ===\n');
fprintf('f(x,y) = (x^2+y-11)^2 + (x+y^2-7)^2\n');
fprintf('알려진 최솟값 4개: (3,2), (-2.805,3.131), (-3.779,-3.283), (3.584,-1.848)\n\n');

himmel = @(v) (v(1)^2 + v(2) - 11)^2 + (v(1) + v(2)^2 - 7)^2;

% 등고선 시각화
[X, Y] = meshgrid(-5:0.05:5, -5:0.05:5);
Z = (X.^2 + Y - 11).^2 + (X + Y.^2 - 7).^2;

figure('Name', '예시 3: Himmelblau 함수');
subplot(1,2,1);
contourf(X, Y, Z, 30, 'LineColor', 'none'); colorbar;
title('등고선 (색이 진할수록 낮음)'); xlabel('x'); ylabel('y');

subplot(1,2,2);
surf(X, Y, log(Z+1), 'EdgeColor', 'none'); view(45, 45);
title('3D 표면 (log 스케일)'); xlabel('x'); ylabel('y');

% 4가지 초기값
init_pts = [0, 0; -1, 3; -3, -3; 4, -2];
opts = optimset('TolFun', 1e-10, 'TolX', 1e-10, 'Display', 'off');

fprintf('%-15s %-20s %-12s %-6s\n', '초기값', '수렴점', 'f(x,y)', 'flag');
fprintf('%s\n', repmat('-', 1, 58));
for i = 1:4
    [xi, fi, flagi] = fminsearch(himmel, init_pts(i,:), opts);
    fprintf('(%2.0f,%2.0f)         (%.3f, %.3f)     %.2e    %d\n', ...
        init_pts(i,1), init_pts(i,2), xi(1), xi(2), fi, flagi);
end
fprintf('\n→ 같은 함수인데 초기값에 따라 다른 최솟값 수렴!\n\n');

%% ========================================================
%  학생 실습 정답
% =========================================================
fprintf('=== 실습 문제 3 정답: 2변수 함수 최솟값 ===\n');
f3 = @(v) (v(1)-2)^4 + (v(1)-2*v(2))^2;
[x3_opt, f3_val] = fminsearch(f3, [0, 0]);
fprintf('최솟점: x=%.6f, y=%.6f\n', x3_opt(1), x3_opt(2));
fprintf('최솟값: f=%.2e\n\n', f3_val);

fprintf('=== 실습 문제 4 정답: sin 모델 커브피팅 ===\n');
x_d = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0];
y_d = [0.3, 1.8, 2.1, 1.2, -0.5, -1.9, -2.0];
sin_model = @(p, x) p(1)*sin(p(2)*x + p(3));
sin_obj   = @(p) sum((y_d - sin_model(p, x_d)).^2);
[p4, rss4] = fminsearch(sin_obj, [2, 2, 0]);
fprintf('a=%.4f,  b=%.4f,  c=%.4f\n', p4(1), p4(2), p4(3));
fprintf('RSS = %.6f\n\n', rss4);

figure('Name', '실습4: sin 모델 피팅');
x_fine = linspace(0, 3, 200);
plot(x_d, y_d, 'ro', 'MarkerSize', 10, 'LineWidth', 2); hold on;
plot(x_fine, sin_model(p4, x_fine), 'b-', 'LineWidth', 2);
xlabel('x'); ylabel('y');
title(sprintf('y = %.3f·sin(%.3f·x + %.3f)', p4));
legend('데이터', '피팅 모델'); grid on;

%% ========================================================
%  보너스: Himmelblau 함수의 4개 최솟값 모두 찾기
% =========================================================
fprintf('=== 보너스: 4개 최솟값 모두 탐색 ===\n');

% 넓은 그리드에서 여러 초기값 시도
[X_grid, Y_grid] = meshgrid(-4:2:4, -4:2:4);
found_mins = [];

for i = 1:numel(X_grid)
    x0_i = [X_grid(i), Y_grid(i)];
    [xi, fi] = fminsearch(himmel, x0_i, opts);
    if fi < 1e-5  % 실제 최솟값 근방
        % 중복 제거 (거리 0.1 이내)
        if isempty(found_mins) || min(sqrt(sum((found_mins - xi).^2, 2))) > 0.1
            found_mins = [found_mins; xi]; %#ok<AGROW>
        end
    end
end

fprintf('발견된 최솟값:\n');
for k = 1:size(found_mins, 1)
    fprintf('  (%.4f, %.4f)  f=%.2e\n', found_mins(k,1), found_mins(k,2), ...
        himmel(found_mins(k,:)));
end
