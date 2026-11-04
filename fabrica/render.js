const {chromium}=require('playwright');const {spawn}=require('child_process');const fs=require('fs');
const mode=process.argv[2]; // 'preview' or 'video'
const seg=fs.existsSync(process.env.SEG||'seg.json')?JSON.parse(fs.readFileSync(process.env.SEG||'seg.json')):null;
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('http://127.0.0.1:8765'+(process.env.PAGE||'/video/video.html')+'?render=1');await p.waitForTimeout(1500);
const cfg=process.env.CFG?JSON.parse(fs.readFileSync(process.env.CFG)):null;
if(cfg){await p.evaluate(c=>{window.CFG=c;window.applyCfg();},cfg);await p.waitForTimeout(2500);}
if(seg) await p.evaluate(s=>{window.SEG=s},seg);
await p.evaluate(()=>{const d=document.getElementById('fr').contentDocument;d.getAnimations().forEach(a=>a.pause());d.documentElement.style.scrollBehavior='auto'});
for(let i=0;i<20&&!(await p.evaluate(()=>window.ready()));i++)await p.waitForTimeout(300);console.log('ready',await p.evaluate(()=>window.ready()));
const END=await p.evaluate(()=>window.render(0));
if(mode==='preview'){const ts=process.argv.slice(3).map(Number);for(const t of ts){await p.evaluate(t=>window.render(t),t);await p.waitForTimeout(60);await p.screenshot({path:`prev_${t}.jpg`,type:'jpeg',quality:70});}await b.close();return;}
const fps=30,N=Math.ceil(END*fps);console.log('frames',N,'dur',END);
const ff=spawn('ffmpeg',['-y','-f','image2pipe','-framerate',String(fps),'-i','-','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',process.env.OUT||'silent.mp4'],{stdio:['pipe','ignore','inherit']});
for(let i=0;i<N;i++){await p.evaluate(t=>window.render(t),i/fps);const buf=await p.screenshot({type:'jpeg',quality:92});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(i%60==0)console.log(i);}
ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();})();
