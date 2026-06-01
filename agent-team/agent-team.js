/**
 * Life Command System - Self-Improving Agent Team
 *
 * 실행: node agent-team.js [run|report|improve|search]
 * 전체 파이프라인: node agent-team.js run
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const CONFIG = {
  ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY || '',
  SLACK_BOT_TOKEN: process.env.SLACK_BOT_TOKEN || 'xoxb-11192160617749-11210448579094-3SLkUfVn1AEzCXWxDGAKrkEj',
  SLACK_CHANNEL: 'claude-code-life-automation',
  SITE_PATH: path.join(__dirname, '..', 'life-system', 'index.html'),
  LOG_PATH: path.join(__dirname, 'agent-log.json'),
  MODEL: 'claude-sonnet-4-6',
};

// ─── Slack ───────────────────────────────────────────────────────────────────

function slackPost(endpoint, body) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body);
    const req = https.request({
      hostname: 'slack.com',
      path: `/api/${endpoint}`,
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${CONFIG.SLACK_BOT_TOKEN}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
      },
    }, (res) => {
      let raw = '';
      res.on('data', d => raw += d);
      res.on('end', () => resolve(JSON.parse(raw)));
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

async function ensureChannel() {
  // 채널 생성 (이미 있으면 ok: false 반환되지만 무시)
  const create = await slackPost('conversations.create', {
    name: CONFIG.SLACK_CHANNEL,
    is_private: false,
  });

  if (create.ok) {
    console.log(`✅ Slack 채널 생성됨: #${CONFIG.SLACK_CHANNEL}`);
    return create.channel.id;
  }

  // 이미 존재하면 목록에서 찾기
  const list = await slackPost('conversations.list', { limit: 200 });
  if (list.ok) {
    const ch = list.channels.find(c => c.name === CONFIG.SLACK_CHANNEL);
    if (ch) return ch.id;
  }
  throw new Error('Slack 채널을 찾거나 생성할 수 없음');
}

async function sendSlack(channelId, blocks, text) {
  return slackPost('chat.postMessage', {
    channel: channelId,
    text,
    blocks,
  });
}

// ─── Claude API ──────────────────────────────────────────────────────────────

function claudeCall(systemPrompt, userMessage) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model: CONFIG.MODEL,
      max_tokens: 4096,
      system: systemPrompt,
      messages: [{ role: 'user', content: userMessage }],
    });

    const req = https.request({
      hostname: 'api.anthropic.com',
      path: '/v1/messages',
      method: 'POST',
      headers: {
        'x-api-key': CONFIG.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
      },
    }, (res) => {
      let raw = '';
      res.on('data', d => raw += d);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(raw);
          if (parsed.error) reject(new Error(parsed.error.message));
          else resolve(parsed.content[0].text);
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// ─── 에이전트 정의 ────────────────────────────────────────────────────────────

const AGENTS = {

  // 1. Researcher: 웹 트렌드 분석 (Claude 지식 기반)
  async researcher(siteContent) {
    console.log('\n🔍 [Researcher] 최신 라이프 자동화 트렌드 분석 중...');
    const system = `당신은 라이프 자동화 시스템 트렌드 연구자입니다.
현재 사이트의 기능을 분석하고, 추가할 수 있는 최신 자동화 아이디어를 찾습니다.
JSON 형식으로만 답하세요.`;

    const result = await claudeCall(system, `
현재 Life Command System 사이트 내용:
${siteContent.slice(0, 3000)}

다음을 JSON으로 반환:
{
  "trends": ["트렌드1", "트렌드2", "트렌드3"],
  "missing_features": ["현재 사이트에 없는 기능1", "기능2", "기능3"],
  "improvement_areas": ["개선 가능 영역1", "영역2"],
  "priority_recommendation": "가장 먼저 추가해야 할 기능 1가지 (이유 포함)"
}
`);
    return JSON.parse(result.match(/\{[\s\S]*\}/)[0]);
  },

  // 2. Improver: 구체적 개선안 도출
  async improver(siteContent, researchResult) {
    console.log('\n⚡ [Improver] 구체적 개선안 도출 중...');
    const system = `당신은 웹 UI/UX 개선 전문가입니다.
연구 결과를 바탕으로 Life Command System에 추가할 구체적인 HTML/CSS/JS 코드를 제안합니다.`;

    const result = await claudeCall(system, `
연구 결과: ${JSON.stringify(researchResult, null, 2)}

현재 사이트 구조 (앞부분):
${siteContent.slice(0, 2000)}

다음을 제안해주세요:
1. 추가할 기능 1가지 (가장 임팩트 있는 것)
2. 그 기능의 구체적인 HTML 코드 스니펫
3. 추가 위치 (어디에 삽입할지)
4. 예상 효과

형식:
FEATURE: [기능명]
LOCATION: [삽입 위치]
EFFECT: [예상 효과]
CODE:
\`\`\`html
[코드]
\`\`\`
`);
    return result;
  },

  // 3. Devil's Advocate: 실패 시나리오 점검
  async devilsAdvocate(improverResult) {
    console.log('\n😈 [Devil\'s Advocate] 3개월 후 실패 시나리오 점검...');
    const system = `당신은 Devil's Advocate입니다.
3개월 후 시점(2026-09-01)에서 역할극을 합니다.
날짜, 상황, 감정을 포함한 구체적 실패 시나리오만 출력합니다.`;

    return await claudeCall(system, `
제안된 개선사항:
${improverResult}

이 개선사항이 실패하는 구체적 시나리오를 3개 제시하세요.
형식: [날짜] [상황] [감정] [실패 원인]
`);
  },

  // 4. Reporter: Slack 보고서 생성 및 전송
  async reporter(research, improvement, devilsAdvocate, channelId) {
    console.log('\n📨 [Reporter] Slack 보고서 전송 중...');

    const now = new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });
    const version = loadLog().version + 1;

    const blocks = [
      {
        type: 'header',
        text: { type: 'plain_text', text: `🤖 Life System Agent Report v${version}` }
      },
      {
        type: 'context',
        elements: [{ type: 'mrkdwn', text: `📅 ${now}` }]
      },
      { type: 'divider' },
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `*🔍 Researcher 발견*\n우선 추가 기능: *${research.priority_recommendation}*\n누락 기능: ${research.missing_features.join(', ')}`
        }
      },
      { type: 'divider' },
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `*⚡ Improver 제안*\n${improvement.slice(0, 800)}`
        }
      },
      { type: 'divider' },
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `*😈 Devil's Advocate 경고*\n${devilsAdvocate.slice(0, 500)}`
        }
      },
      {
        type: 'actions',
        elements: [
          {
            type: 'button',
            text: { type: 'plain_text', text: '✅ 개선사항 적용' },
            style: 'primary',
            value: 'apply'
          },
          {
            type: 'button',
            text: { type: 'plain_text', text: '🔄 다시 분석' },
            value: 'retry'
          }
        ]
      }
    ];

    await sendSlack(channelId, blocks, `Life System Agent Report v${version}`);
    console.log('✅ Slack 전송 완료!');

    // 로그 저장
    saveLog({ version, timestamp: now, research, improvement: improvement.slice(0, 500) });
  }
};

// ─── 로그 관리 ────────────────────────────────────────────────────────────────

function loadLog() {
  try {
    return JSON.parse(fs.readFileSync(CONFIG.LOG_PATH, 'utf-8'));
  } catch {
    return { version: 0, history: [] };
  }
}

function saveLog(entry) {
  const log = loadLog();
  log.version = entry.version;
  log.history = [entry, ...(log.history || [])].slice(0, 20);
  fs.writeFileSync(CONFIG.LOG_PATH, JSON.stringify(log, null, 2));
}

// ─── 메인 파이프라인 ──────────────────────────────────────────────────────────

async function run() {
  console.log('━'.repeat(50));
  console.log('🚀 Life System Agent Team 시작');
  console.log('━'.repeat(50));

  // API 키 확인
  if (!CONFIG.ANTHROPIC_API_KEY) {
    console.error('❌ ANTHROPIC_API_KEY가 없습니다. settings.json을 확인하세요.');
    process.exit(1);
  }

  // Slack 채널 확인/생성
  let channelId;
  try {
    channelId = await ensureChannel();
    console.log(`✅ Slack 채널 준비됨 (ID: ${channelId})`);
  } catch (e) {
    console.error('❌ Slack 연결 실패:', e.message);
    process.exit(1);
  }

  // 사이트 읽기
  const siteContent = fs.readFileSync(CONFIG.SITE_PATH, 'utf-8');
  console.log(`✅ 사이트 로드됨 (${(siteContent.length / 1024).toFixed(1)}KB)`);

  // 에이전트 파이프라인 실행
  const research = await AGENTS.researcher(siteContent);
  console.log('  발견:', research.priority_recommendation);

  const improvement = await AGENTS.improver(siteContent, research);
  console.log('  개선안 도출 완료');

  const devilCheck = await AGENTS.devilsAdvocate(improvement);
  console.log('  리스크 점검 완료');

  await AGENTS.reporter(research, improvement, devilCheck, channelId);

  console.log('\n━'.repeat(50));
  console.log('✅ 모든 에이전트 완료! Slack을 확인하세요.');
  console.log('━'.repeat(50));
}

// 단일 에이전트 실행
async function runSingle(agentName) {
  const siteContent = fs.readFileSync(CONFIG.SITE_PATH, 'utf-8');
  switch (agentName) {
    case 'research':
      const r = await AGENTS.researcher(siteContent);
      console.log(JSON.stringify(r, null, 2));
      break;
    case 'improve':
      const research = await AGENTS.researcher(siteContent);
      const i = await AGENTS.improver(siteContent, research);
      console.log(i);
      break;
    default:
      console.log('사용법: node agent-team.js [run|research|improve]');
  }
}

// 진입점
const cmd = process.argv[2] || 'run';
if (cmd === 'run') run().catch(console.error);
else runSingle(cmd).catch(console.error);
