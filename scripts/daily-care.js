#!/usr/bin/env node
// 主动关心脚本 - 黛玉的温馨问候
// 定期检查主人状态，发送关心消息

const { execSync } = require('child_process');
const fs = require('fs');

const LOG_FILE = '/Users/zhuxiaolei/.openclaw/workspace/logs/care.log';
const WECHAT_USER = 'o9cq80-VOQWTsN3h5bn6gyR2IdY4@im.wechat';
const ACCOUNT_ID = 'ec25a54ce939-im-bot';

function log(message) {
    const timestamp = new Date().toLocaleString('zh-CN', { hour12: false });
    fs.appendFileSync(LOG_FILE, `[${timestamp}] ${message}\n`);
}

function getHourlyCare() {
    const hour = new Date().getHours();
    const weekday = new Date().getDay();
    
    // 工作时间（周一至周五 9-12 点、14-18 点）
    const isWorkHour = (weekday >= 1 && weekday <= 5) && 
                       ((hour >= 9 && hour < 12) || (hour >= 14 && hour < 18));
    
    const careMessages = {
        9: {
            text: '🌸 主人，上午好呀～\n\n新的一天开始了，黛玉祝您今天工作顺利！\n\n记得喝杯温水，开启活力满满的一天哦～ 💕',
            type: 'morning'
        },
        10: {
            text: '🌸 主人，工作一小时啦～\n\n黛玉提醒您：\n• 起身活动一下筋骨\n• 眺望远方，放松眼睛\n• 喝口水，休息一下\n\n身体是革命的本钱，别太累着自己～ 💕',
            type: 'rest'
        },
        11: {
            text: '🌸 主人，快到午饭时间啦～\n\n再坚持一下就休息吧！\n\n黛玉已经想好中午吃什么了吗？要按时吃饭，别饿着肚子哦～ 🍚',
            type: 'lunch'
        },
        14: {
            text: '🌸 主人，下午好呀～\n\n午休过后，精神饱满地继续工作吧！\n\n黛玉为您加油打气，今天的目标一定能完成～ 💪🌸',
            type: 'afternoon'
        },
        15: {
            text: '🌸 主人，下午茶时间到～\n\n工作辛苦了，起来走动走动吧～\n\n• 伸个懒腰\n• 泡杯茶或咖啡\n• 吃点小零食\n\n补充能量，继续加油！💕',
            type: 'rest'
        },
        16: {
            text: '🌸 主人，再坚持一下～\n\n离下班不远啦，今天的工作进展如何？\n\n如果有需要帮忙的地方，尽管吩咐黛玉哦～ 🌸',
            type: 'encourage'
        },
        17: {
            text: '🌸 主人，傍晚时分～\n\n今天的客户开发工作要开始啦！\n\n黛玉已经准备好协助您了，需要我帮忙做什么吗？\n• 整理客户资料\n• 写开发信\n• 市场调研\n\n随时吩咐～ 💕',
            type: 'work'
        },
        20: {
            text: '🌸 主人，晚上好～\n\n忙碌一天，辛苦啦！\n\n该休息一下了，黛玉建议：\n• 看看电影放松\n• 打局 LOLM 娱乐\n• 或者早点休息\n\n别工作太晚，身体要紧～ 💕',
            type: 'evening'
        },
        22: {
            text: '🌸 主人，夜深啦～\n\n该准备休息了，熬夜对身体不好哦。\n\n黛玉祝您今晚做个好梦，明天又是美好的一天～\n\n晚安，主人 🌙💕',
            type: 'goodnight'
        }
    };
    
    return careMessages[hour] || null;
}

function sendMessage(message) {
    try {
        const escapedMessage = message.replace(/'/g, "'\\''");
        const cmd = `/opt/homebrew/bin/openclaw message send -t '${WECHAT_USER}' --channel openclaw-weixin --account '${ACCOUNT_ID}' -m '${escapedMessage}'`;
        execSync(cmd, { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] });
        return true;
    } catch (error) {
        log('发送失败：' + error.message);
        return false;
    }
}

// 检查是否需要发送（避免重复）
function shouldSend(type) {
    const stateFile = '/tmp/care-state.json';
    let state = {};
    
    try {
        state = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
    } catch (e) {
        state = {};
    }
    
    const today = new Date().toDateString();
    const lastSent = state[type];
    
    // 如果今天已经发过同类型的消息，就不再发
    if (lastSent && lastSent === today) {
        return false;
    }
    
    // 更新状态
    state[type] = today;
    fs.writeFileSync(stateFile, JSON.stringify(state));
    
    return true;
}

async function main() {
    log('开始关心检查...');
    
    const care = getHourlyCare();
    
    if (!care) {
        log('当前时段无需关心消息');
        return;
    }
    
    if (!shouldSend(care.type)) {
        log(`今天已发送过 ${care.type} 类型的消息，跳过`);
        return;
    }
    
    log(`发送 ${care.type} 类型关心消息`);
    const success = await sendMessage(care.text);
    
    if (success) {
        log('关心消息发送成功');
    } else {
        log('关心消息发送失败');
    }
    
    log('关心检查完成');
}

main();
