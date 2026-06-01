%% MATLAB 4대 함수 씹어먹기 — 파트 2: fzero
% 강의 실습 스크립트 | 실행: F5 또는 섹션별 Ctrl+Enter

%% ========================================================
%  섹션 0: fzero 기본 문법 데모
% =========================================================
fprintf('=== fzero 기본 동작 확인 ===\n');

% 간단한 예: x^2 - 4 = 0 (근: x=2, x=-2)
f_simple = @(x) x.^2 - 4;

[x1, fv1, flag1] = fzero(f_simple, [0, 5]);
[x2, fv2, flag2] = fzero(f_simple, [-5, 0]);

fprintf('양의 근: x = %.6f  (f(x)=%.2e, flag=%d)\n', x1, fv1, flag1);
fprintf('음의 근: x = %.6f  (f(x)=%.2e, flag=%d)\n\n', x2, fv2, flag2);

%% ========================================================
%  예시 1: 손익분기점 찾기
% =========================================================
fprintf('=== 예시 1: 손익분기점 ===\n');
fprintf('R(q)=50q, C(q)=1000+30q+0.1q^2\n');

profit = @(q) 50*q - (1000 + 30*q + 0.1*q.^2);

% 그래프 먼저!
q_range = 0:1:200;
figure('Name', '예시 1: 손익분기점');
plot(q_range, profit(q_range), 'b-', 'LineWidth', 2);
hold on;
yline(0, 'r--', 'LineWidth', 1.5);
xlabel('생산량 q (개)'); ylabel('이익 (만원)');
title('손익분기점 분석');
grid on;

% 그래프에서 근이 2개임을 확인 → 구간 분리
[q1, fv1, flag1] = fzero(profit, [1, 50]);
[q2, fv2, flag2] = fzero(profit, [50, 200]);

plot(q1, 0, 'ro', 'MarkerSize', 12, 'MarkerFaceColor', 'r');
plot(q2, 0, 'go', 'MarkerSize', 12, 'MarkerFaceColor', 'g');
legend('이익 곡선', '기준선(이익=0)', ...
       sprintf('BEP1 q=%.1f', q1), sprintf('BEP2 q=%.1f', q2));

fprintf('손익분기점 1: q = %.2f  (flag=%d)\n', q1, flag1);
fprintf('손익분기점 2: q = %.2f  (flag=%d)\n', q2, flag2);
fprintf('이익 구간: %.1f < q < %.1f\n\n', q1, q2);

%% ========================================================
%  예시 2: 열전달 초월방정식
% =========================================================
fprintf('=== 예시 2: 열전달 초월방정식 ===\n');
fprintf('tanh(mL) / (mL) = 0.8\n');

heat_eq = @(x) tanh(x)./x - 0.8;

% 그래프 확인
x_range = 0.01:0.01:5;
figure('Name', '예시 2: 열전달 방정식');
plot(x_range, heat_eq(x_range), 'b-', 'LineWidth', 2);
hold on;
yline(0, 'r--', 'LineWidth', 1.5);
xlabel('mL'); ylabel('tanh(mL)/mL - 0.8');
title('열전달 방정식의 근 탐색');
grid on; ylim([-1, 0.5]);

[mL_sol, fval, flag] = fzero(heat_eq, [0.1, 5]);
plot(mL_sol, 0, 'ro', 'MarkerSize', 12, 'MarkerFaceColor', 'r');

fprintf('mL 해: %.6f\n', mL_sol);
fprintf('검증: f(mL) = %.2e  (0에 가까울수록 정확)\n', fval);
fprintf('핀 효율: %.6f  (목표: 0.8000)\n', tanh(mL_sol)/mL_sol);
fprintf('exitflag: %d\n\n', flag);

%% ========================================================
%  예시 3: 초기값 선택의 중요성
% =========================================================
fprintf('=== 예시 3: 초기값 선택의 중요성 ===\n');

f3 = @(x) x.^3 - 6*x.^2 + 11*x - 6;  % (x-1)(x-2)(x-3)

% 그래프
x_range3 = 0:0.01:4;
figure('Name', '예시 3: 초기값 의존성');
plot(x_range3, f3(x_range3), 'b-', 'LineWidth', 2);
hold on;
yline(0, 'r--', 'LineWidth', 1.5);
scatter([1,2,3], [0,0,0], 120, 'ro', 'filled');
xlabel('x'); ylabel('f(x)');
title('f(x) = (x-1)(x-2)(x-3)의 세 근');
grid on;

% 각기 다른 초기값
fprintf('%-12s %-12s %-8s\n', '초기값', '수렴점', 'exitflag');
fprintf('%s\n', repmat('-', 1, 35));

init_vals = {0.5, 1.8, 2.8};
for k = 1:3
    [xi, ~, fi] = fzero(f3, init_vals{k});
    fprintf('x0 = %-6.1f → x = %.4f  (flag=%d)\n', init_vals{k}, xi, fi);
end

fprintf('\n안전한 방법 — 구간 지정:\n');
[x_safe, fv_safe, flag_safe] = fzero(f3, [1.5, 2.5]);
fprintf('fzero(f, [1.5, 2.5]) → x = %.4f  (flag=%d)\n\n', x_safe, flag_safe);

%% ========================================================
%  학생 실습 정답
% =========================================================
fprintf('=== 실습 문제 1 정답: e^x - 3x = 0 ===\n');
f_ex = @(x) exp(x) - 3*x;

% 그래프 확인
figure('Name', '실습1: e^x - 3x = 0');
fplot(f_ex, [0, 3], 'b-', 'LineWidth', 2);
hold on; yline(0, 'r--'); grid on;
title('e^x - 3x = 0'); xlabel('x'); ylabel('f(x)');

[x1_ex, ~, f1_ex] = fzero(f_ex, [0, 1]);
[x2_ex, ~, f2_ex] = fzero(f_ex, [1, 2]);
fprintf('근 1: x = %.6f  (flag=%d)\n', x1_ex, f1_ex);
fprintf('근 2: x = %.6f  (flag=%d)\n\n', x2_ex, f2_ex);

fprintf('=== 실습 문제 2 정답: 탱크 방정식 ===\n');
tank = @(t) t - 100*(1 - exp(-t/50)) - 30;
[t_sol, fval_tank, flag_tank] = fzero(tank, [0, 200]);
fprintf('t = %.4f초\n', t_sol);
fprintf('f(t) = %.2e, flag = %d\n', fval_tank, flag_tank);
