%% MATLAB 4대 함수 씹어먹기 — 파트 1: min / max
% 강의 실습 스크립트 | 실행: F5 또는 섹션별 Ctrl+Enter

%% ========================================================
%  섹션 0: 벡터화 성능 비교 (루프 vs min)
% =========================================================
fprintf('=== 성능 비교: 루프 vs min ===\n');

data = rand(1, 1000000);

tic
current_min = data(1);
for k = 2:length(data)
    if data(k) < current_min
        current_min = data(k);
    end
end
t_loop = toc;

tic
best_min = min(data);
t_vec = toc;

fprintf('루프 방식: %.4f초\n', t_loop);
fprintf('min()  : %.4f초\n', t_vec);
fprintf('속도 차이: %.0f배\n\n', t_loop / t_vec);

%% ========================================================
%  섹션 1: 문법 패턴 5가지 데모
% =========================================================
fprintf('=== 패턴 1: 기본 ===\n');
A = [3, 1, 4, 1, 5, 9, 2, 6];
fprintf('A = %s\n', mat2str(A));
fprintf('min(A) = %d,  max(A) = %d\n\n', min(A), max(A));

fprintf('=== 패턴 2: 인덱스 반환 ===\n');
[m, i] = min(A);
fprintf('[m,i] = min(A) → m=%d, i=%d\n', m, i);
[~, j] = max(A);
fprintf('[~,j] = max(A) → j=%d  (값은 버림)\n\n', j);

fprintf('=== 패턴 3: 행렬 방향 ===\n');
B = [1, 5, 3; 4, 2, 6; 7, 8, 0];
disp('B ='); disp(B);
fprintf('min(B)           = %s  (열 방향)\n', mat2str(min(B)));
fprintf('min(B,[],2)      = %s  (행 방향)\n', mat2str(min(B,[],2)));
fprintf('min(B,[],"all")  = %d  (전체)\n\n', min(B,[],'all'));

fprintf('=== 패턴 4: omitnan ===\n');
C = [3, NaN, 7, 2, NaN, 5];
fprintf('C = %s\n', mat2str(C));
fprintf('min(C)            = %s  (NaN 전파)\n', num2str(min(C)));
fprintf('min(C,"omitnan")  = %d  (NaN 무시)\n\n', min(C,'omitnan'));

fprintf('=== 패턴 5: 비교형 / 클리핑 ===\n');
X = [1, 8, 3];
Y = [5, 2, 6];
fprintf('X=%s, Y=%s\n', mat2str(X), mat2str(Y));
fprintf('min(X,Y) = %s\n', mat2str(min(X,Y)));
data_clip = [10, 85, 23, 110, 67];
fprintf('min([10,85,23,110,67], 100) = %s  (클리핑)\n\n', mat2str(min(data_clip,100)));

%% ========================================================
%  예시 1: 센서 온도 데이터
% =========================================================
fprintf('=== 예시 1: 센서 온도 데이터 ===\n');

temperature = [12.3, 11.8, 11.2, 10.9, 10.5, 10.8, ...
               11.5, 13.2, 15.6, 18.3, 21.0, 23.4, ...
               25.1, 26.8, 27.2, 27.5, 26.9, 25.3, ...
               23.1, 20.7, 18.4, 16.2, 14.5, 13.1];

[T_max, idx_max] = max(temperature);
[T_min, idx_min] = min(temperature);
hour_max = idx_max - 1;
hour_min = idx_min - 1;

fprintf('최고 온도: %.1f°C  (%d시)\n', T_max, hour_max);
fprintf('최저 온도: %.1f°C  (%d시)\n', T_min, hour_min);
fprintf('일교차: %.1f°C\n\n', T_max - T_min);

figure('Name', '예시 1: 일별 기온');
hours = 0:23;
plot(hours, temperature, '-o', 'LineWidth', 1.5, 'Color', [0.2 0.5 0.8]);
hold on;
plot(hour_max, T_max, 'rv', 'MarkerSize', 14, 'MarkerFaceColor', 'r');
plot(hour_min, T_min, 'b^', 'MarkerSize', 14, 'MarkerFaceColor', 'b');
xlabel('시각 (시)'); ylabel('온도 (°C)');
title('일별 기온 변화');
legend('온도', sprintf('최고 %.1f°C (%d시)', T_max, hour_max), ...
       sprintf('최저 %.1f°C (%d시)', T_min, hour_min));
grid on; xlim([-1, 24]);

%% ========================================================
%  예시 2: 가격 비교 행렬
% =========================================================
fprintf('=== 예시 2: 가격 비교 행렬 ===\n');

price = [120, 115, 130, 108;
         250, 245, 260, 255;
          89,  92,  85,  91;
         340, 320, 335, 315;
          55,  58,  52,  60];

product_names = {'상품A', '상품B', '상품C', '상품D', '상품E'};
company_names = {'A마트', 'B마트', 'C마트', 'D마트'};

[min_prices, best_idx] = min(price, [], 2);

fprintf('%-6s | %-10s | %-6s\n', '상품', '최저가(천원)', '마트');
fprintf('%s\n', repmat('-', 1, 28));
for k = 1:5
    fprintf('%-6s | %10.0f | %s\n', ...
        product_names{k}, min_prices(k), company_names{best_idx(k)});
end

[~, prod_idx] = min(min_prices);
fprintf('\n전체 최저: %s의 %s (%d천원)\n\n', ...
    company_names{best_idx(prod_idx)}, product_names{prod_idx}, min_prices(prod_idx));

%% ========================================================
%  예시 3: NaN 데이터 처리
% =========================================================
fprintf('=== 예시 3: NaN 데이터 처리 ===\n');

pm25 = [35.2, NaN, 42.1, 38.7, NaN, 51.3, 29.6];
days = {'월', '화', '수', '목', '금', '토', '일'};

fprintf('NaN 포함 min: %s\n', num2str(min(pm25)));

[clean_min, idx_min] = min(pm25, 'omitnan');
[clean_max, idx_max] = max(pm25, 'omitnan');
nan_count = sum(isnan(pm25));

fprintf('최저 PM2.5: %.1f µg/m³ (%s요일)\n', clean_min, days{idx_min});
fprintf('최고 PM2.5: %.1f µg/m³ (%s요일)\n', clean_max, days{idx_max});
fprintf('결측률: %.1f%% (%d/%d일)\n', nan_count/length(pm25)*100, nan_count, length(pm25));
fprintf('확인: pm25(%d) = %.1f\n\n', idx_min, pm25(idx_min));

figure('Name', '예시 3: PM2.5 데이터');
day_idx = 1:7;
bar(day_idx, pm25, 'FaceColor', [0.6 0.8 0.4]);
hold on;
plot(idx_min, clean_min, 'bv', 'MarkerSize', 14, 'MarkerFaceColor', 'b');
plot(idx_max, clean_max, 'r^', 'MarkerSize', 14, 'MarkerFaceColor', 'r');
set(gca, 'XTickLabel', days, 'XTick', 1:7);
xlabel('요일'); ylabel('PM2.5 (µg/m³)');
title('주간 PM2.5 측정값 (NaN = 센서 오류)');
legend('PM2.5', '최저', '최고'); grid on;

%% ========================================================
%  학생 실습 정답
% =========================================================
fprintf('=== 실습 문제 1 정답 ===\n');
scores = [78, 92, 65, 88, 95, 71, 83, 59, 100, 76];
[top, top_idx] = max(scores);
fprintf('최고: %d점 (학생 %d번)\n', top, top_idx);
fprintf('최저: %d점\n', min(scores));
fprintf('범위: %d점\n\n', max(scores) - min(scores));

fprintf('=== 실습 문제 2 정답 ===\n');
sales = [120, 135, NaN, 142, 118;
          98, NaN, 103,  NaN, 115;
         205, 198, 212, 195, NaN];
branch = {'지점1','지점2','지점3'};
day_names = {'월','화','수','목','금'};
for b = 1:3
    [pk, d] = max(sales(b,:), 'omitnan');
    fprintf('%s 최대: %d개 (%s요일)\n', branch{b}, pk, day_names{d});
end
fprintf('전체 최솟값 (NaN 제외): %d\n', min(sales(:), 'omitnan'));
