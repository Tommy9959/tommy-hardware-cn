const { WechatyBuilder } = require('wechaty')

const bot = WechatyBuilder.build({
  name: 'openclaw-wechat',
  puppet: 'wechaty-puppet-wechat4u',
})

bot.on('scan', (qrcode, status) => {
  console.log(`\n[${new Date().toLocaleString('zh-CN')}] 扫码登录：`)
  console.log(`状态：${status}`)
  console.log(`二维码：https://wechaty.js.org/qrcode/${encodeURIComponent(qrcode)}`)
  console.log('\n请用手机微信扫描二维码登录\n')
})

bot.on('login', user => {
  console.log(`\n✅ 登录成功：${user.name()} (${user.id})\n`)
})

bot.on('logout', user => {
  console.log(`\n❌ 已退出：${user.name()}\n`)
})

bot.on('message', async message => {
  const contact = message.talker()
  const text = message.text()
  const room = message.room()
  
  console.log(`[${new Date().toLocaleString('zh-CN')}] ${room ? `[群：${await room.topic()}] ` : ''}${contact.name()}: ${text}`)
  
  // 简单的自动回复测试
  if (text === '测试' || text === 'test') {
    await contact.say('收到！WeChaty 运行正常 🌸')
  }
})

bot.on('error', error => {
  console.error(`\n❌ 错误：${error.message}\n`)
})

async function main() {
  console.log('🌸 林黛玉微信助手启动中...\n')
  await bot.start()
  console.log('等待扫码登录...')
}

main().catch(console.error)
