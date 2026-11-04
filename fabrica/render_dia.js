// Render del video «Día X» (video_dia_ruleta.html). Uso:
// CFG=cfg.json SEG=seg.json OUT=silent.mp4 node render_dia.js video|preview [t1 t2 ...]
// Requiere la carpeta de trabajo servida en http://127.0.0.1:8765 (python3 -m http.server 8765).
const {chromium}=require('playwright');const {spawn}=require('child_process');const fs=require('fs');
const mode=process.argv[2];const cfg=JSON.parse(fs.readFileSync(process.env.CFG||'cfg.json'));const seg=JSON.parse(fs.readFileSync(process.env.SEG||'seg.json'));
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('http://127.0.0.1:8765'+(process.env.PAGE||'/video.html')+'?render=1');await p.waitForTimeout(800);
await p.evaluate(([c,s])=>{window.CFG=c;window.SEG=s;window.applyCfg()},[cfg,seg]);await p.waitForTimeout(2500);
await p.evaluate(()=>{const d=document.getElementById('fr').contentDocument;d.getAnimations().forEach(a=>a.pause());d.documentElement.style.scrollBehavior='auto'});
for(let i=0;i<20&&!(await p.evaluate(()=>window.ready()));i++)await p.waitForTimeout(300);
const END=await p.evaluate(()=>window.render(0));
if(mode==='preview'){for(const t of process.argv.slice(3).map(Number)){await p.evaluate(t=>window.render(t),t);await p.waitForTimeout(50);await p.screenshot({path:`prev_${t}.jpg`,type:'jpeg',quality:70})}await b.close();return}
const fps=30,N=Math.ceil(END*fps);console.log('frames',N);
const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(fps),'-i','-','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',process.env.OUT||'silent.mp4'],{stdio:['pipe','ignore','inherit']});
for(let i=0;i<N;i++){await p.evaluate(t=>window.render(t),i/fps);const buf=await p.screenshot({type:'jpeg',quality:92});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(i%150==0)console.log(i);}
ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();})();
