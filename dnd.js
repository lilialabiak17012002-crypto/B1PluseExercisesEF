// Word bank: sticky bank for every exercise with a bank, plus drag-and-drop / tap-to-place
// for gap-fill exercises whose answers are bank words used as they are.
(function(){
  const LIST=typeof SECS!=='undefined'?SECS:(typeof S!=='undefined'&&Array.isArray(S)?S:null);
  if(!LIST)return;
  const secsEl=document.getElementById('secs');
  const cardOf=si=>secsEl?secsEl.children[si]:document.getElementById('s'+si);
  // accepted answers per gap: {a:[[..],[..]]} or legacy array item whose last element is the answer list
  const answersOf=it=>Array.isArray(it)?(Array.isArray(it[it.length-1])?[it[it.length-1]]:null):(Array.isArray(it.a)?(it.a.length&&!Array.isArray(it.a[0])?[it.a]:it.a):null);
  const css=`
.bank.sticky{position:sticky;top:0;z-index:5;background:var(--paper,#fff);margin:10px -22px 6px;padding:10px 22px;border-bottom:1px solid transparent;transition:box-shadow .15s,border-color .15s}
.bank.sticky.stuck{box-shadow:0 6px 12px -8px rgba(0,0,0,.25);border-color:var(--line,#eee)}
.bank.dnd span{cursor:grab;user-select:none;-webkit-user-select:none;touch-action:none;padding:6px 16px;font-weight:700;
  color:var(--tx);border:2px solid var(--bd);background-color:var(--bg);
  background-image:linear-gradient(var(--fill),var(--fill));background-repeat:no-repeat;background-position:50% 100%;background-size:100% 0%;
  box-shadow:0 2px 0 var(--bd),0 3px 8px rgba(34,48,74,.08);
  transition:background-size .35s ease,color .25s,box-shadow .25s,transform .15s,opacity .15s}
.bank.dnd span:hover,.bank.dnd span.sel{background-size:100% 100%;color:#fff;border-color:var(--fill);transform:translateY(-2px);box-shadow:0 8px 18px -4px var(--fill)}
.bank.dnd span:active{transform:translateY(0);cursor:grabbing}
.bank.dnd span.sel{outline:2px solid var(--fill);outline-offset:3px}
.bank.dnd span.used{opacity:.4;box-shadow:none}
.bank.dnd span.used:hover{background-size:100% 0%;color:var(--tx);border-color:var(--bd);transform:none}
.bank-tip{font-size:13px;color:#8a7f70;margin:-2px 0 6px}
li.q input.slot{cursor:pointer;caret-color:transparent;text-align:center;width:130px;height:36px;box-sizing:border-box;padding:3px 14px;margin:2px 4px;
  border-radius:999px;border:2px dashed #C9D3E3;background:#FAFBFE;font-weight:700;font-size:14px;color:#22304A;vertical-align:middle;transition:transform .15s}
li.q input.slot.filled{border:2px solid var(--bd);background:var(--bg);color:var(--tx);box-shadow:0 2px 0 var(--bd)}
li.q input.slot.over,li.q input.slot.target{border-color:#5A62C9;background:#F3F3FC}
li.q input.slot.over{transform:scale(1.06)}
li.q input.slot.ok1{border:2px solid var(--green,#2e8b57);background:#effaf4;box-shadow:none;color:inherit}
ol.pics{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:14px;padding:4px 0}
@media (max-width:560px){ol.pics{grid-template-columns:1fr 1fr;gap:10px}ol.pics img.pic{width:72px;height:72px}ol.pics li.q{padding:10px 6px}}
ol.pics li.q{border:1px solid var(--line,#E8E1D4);border-radius:18px;padding:14px 10px 12px;display:flex;flex-direction:column;align-items:center;gap:10px;line-height:1.3;background:var(--paper,#fff);text-align:center}
ol.pics li.q::before{display:none}
ol.pics li.q:last-child{border-bottom:1px solid var(--line,#E8E1D4)}
ol.pics img.pic{width:96px;height:96px;object-fit:contain;user-select:none;-webkit-user-drag:none;pointer-events:none}
ol.pics li.q input.slot{width:100%;max-width:150px;margin:0}
ol.pics .fix{margin:0;font-size:14px}
li.q input.slot.bad1{border:2px solid var(--red,#c0392b);background:#fff1f1;box-shadow:none;color:inherit}
.dnd-ghost{position:fixed;z-index:1000;pointer-events:none;background:var(--fill);border:2px solid var(--fill);color:#fff;border-radius:999px;padding:6px 16px;font:700 14px var(--sans,sans-serif);box-shadow:0 12px 24px -6px var(--fill);transform:translate(-50%,-60%) rotate(-3deg)}
`;
  const st=document.createElement('style');st.textContent=css;document.head.append(st);
  const N=typeof norm==='function'?norm:(s=>s.toLowerCase().trim());
  const UA=typeof WHY_LANG!=='undefined'?WHY_LANG!=='en':/^\/a[12]\//.test(location.pathname);
  const PAL=[['#EBC9A2','#FCF3EA','#8A4B0B','#E0913A'],['#E6BCD0','#FBF0F5','#8E3557','#C94F7C'],['#BFD8B8','#F2F8EF','#3F6B21','#3E9150'],
    ['#C3D3F2','#F3F5FD','#4B4CA0','#5A62C9'],['#EDC1BD','#FCF1EF','#8C3A22','#C2553E'],['#D8C4EC','#F8F2FC','#6B3A8C','#8E5BC2'],['#A9D7E0','#EFF8FA','#0E6B5C','#1F8F86']];
  const $id=id=>document.getElementById(id);
  const mkEl=(t,c,txt)=>{const e=document.createElement(t);if(c)e.className=c;if(txt!=null)e.textContent=txt;return e;};
  function sticky(bank){
    bank.classList.add('sticky');
    const sentinel=mkEl('div');bank.before(sentinel);
    new IntersectionObserver(([e])=>bank.classList.toggle('stuck',!e.isIntersecting&&e.boundingClientRect.top<0)).observe(sentinel);
  }
  // drag-and-drop / tap-to-place between the bank chips and slot inputs
  function wire(bank,slots,tipText,onPlace){
    bank.classList.add('dnd');
    bank.after(mkEl('p','bank-tip',tipText));
    const chips=[...bank.querySelectorAll('span')];
    const colorOf={};
    const paint=(el,w)=>{const c=colorOf[w];['--bd','--bg','--tx','--fill'].forEach((v,k)=>c?el.style.setProperty(v,c[k]):el.style.removeProperty(v));};
    chips.forEach((c,i)=>{colorOf[c.textContent]=PAL[i%PAL.length];paint(c,c.textContent);});
    let picked=null;
    const done=inp=>!!inp.closest('li.q').dataset.done;
    const refresh=()=>{const used={};slots.forEach(s=>{s.classList.toggle('filled',!!s.value);paint(s,s.value);if(s.value)used[s.value]=(used[s.value]||0)+1;});
      chips.forEach(c=>c.classList.toggle('used',!!used[c.textContent]));};
    const place=(inp,w)=>{if(done(inp))return;inp.value=w;onPlace&&onPlace(inp,w);refresh();};
    const unpick=()=>{if(picked)picked.classList.remove('sel');picked=null;slots.forEach(s=>s.classList.remove('target'));};
    slots.forEach(s=>{
      s.readOnly=true;s.classList.add('slot');s.setAttribute('inputmode','none');s.placeholder='';
      s.addEventListener('click',()=>{if(done(s))return;
        if(picked){place(s,picked.textContent);unpick();}
        else if(s.value){place(s,'');}});
    });
    chips.forEach(c=>{
      c.addEventListener('pointerdown',e=>{
        if(e.button>0)return;e.preventDefault();
        const x0=e.clientX,y0=e.clientY;let ghost=null,over=null;
        const move=ev=>{
          if(!ghost&&Math.hypot(ev.clientX-x0,ev.clientY-y0)>6){ghost=mkEl('div','dnd-ghost',c.textContent);paint(ghost,c.textContent);document.body.append(ghost);unpick();}
          if(!ghost)return;ghost.style.left=ev.clientX+'px';ghost.style.top=ev.clientY+'px';
          let el=document.elementFromPoint(ev.clientX,ev.clientY);
          // in picture mode the whole card (picture included) accepts the drop
          if(el&&!slots.includes(el)){const li=el.closest&&el.closest('ol.pics li.q');if(li)el=li.querySelector('input.slot');}
          const t=el&&slots.includes(el)&&!done(el)?el:null;
          if(t!==over){over&&over.classList.remove('over');over=t;over&&over.classList.add('over');}
          if(ev.clientY>innerHeight-50)scrollBy(0,14);else if(ev.clientY<50)scrollBy(0,-14);
        };
        const up=()=>{removeEventListener('pointermove',move);removeEventListener('pointerup',up);removeEventListener('pointercancel',up);
          if(ghost){ghost.remove();if(over){over.classList.remove('over');place(over,c.textContent);}}
          else{const was=picked===c;unpick();if(!was){picked=c;c.classList.add('sel');slots.forEach(s=>{if(!done(s))s.classList.add('target');});}}
        };
        addEventListener('pointermove',move);addEventListener('pointerup',up);addEventListener('pointercancel',up);
      });
    });
    const again=$id('again');if(again)again.addEventListener('click',()=>{unpick();slots.forEach(s=>{s.readOnly=true;s.value='';s.classList.remove('ok1','bad1');});refresh();});
    const check=$id('check');if(check)check.addEventListener('click',unpick);
  }
  LIST.forEach((sec,si)=>{
    const card=cardOf(si);if(!card)return;
    // picture matching: a match exercise with sec.pics = {word: image url}
    if(sec.type==='match'&&sec.pics&&Array.isArray(sec.items[0])){
      const ol=card.querySelector('ol');if(!ol)return;
      const words=sec.items.map(it=>it[0]);
      const bank=mkEl('div','bank');words.slice().sort((a,b)=>a.localeCompare(b)).forEach(w=>bank.append(mkEl('span','',w)));
      ol.before(bank);sticky(bank);ol.classList.add('pics');
      const slots=[];
      [...ol.querySelectorAll('li.q')].forEach((li,i)=>{
        const w=words[i];const sel=li.querySelector('select');
        [...li.children].forEach(ch=>{if(!ch.classList.contains('fix'))ch.style.display='none';});
        const img=mkEl('img','pic');img.src=sec.pics[w];img.alt='';img.loading='lazy';img.draggable=false;
        const inp=mkEl('input');inp.type='text';inp.autocomplete='off';inp._sel=sel;
        li.prepend(img,inp);slots.push(inp);
        li.style.cursor='pointer';li.addEventListener('click',e=>{if(e.target!==inp&&!e.target.closest('.fix'))inp.click();});
      });
      wire(bank,slots,UA?'Перетягни слово під картинку або натисни на слово, а потім на картинку.':'Drag a word under the picture, or tap a word and then a picture.',
        (inp,w)=>{const it=sec.items.find(x=>x[0]===w);inp._sel.value=it?it[1]:'';});
      const check=$id('check');if(check)check.addEventListener('click',()=>{
        [...ol.querySelectorAll('li.q')].forEach((li,i)=>{const inp=slots[i];const ok=li.classList.contains('ok');
          inp.classList.add(ok?'ok1':'bad1');
          const fix=li.querySelector('.fix');if(!ok&&inp.value){fix.textContent=(UA?'✗ Правильно: ':'✗ Correct answer: ')+words[i];}});});
      return;
    }
    if(!sec.bank)return;
    const bank=card.querySelector('.bank');if(!bank)return;
    sticky(bank);
    if(sec.type==='match'||sec.type==='choice'||sec.type==='order')return;
    const words=sec.bank.map(N);
    const ok=sec.items.every(it=>{const A=answersOf(it);return A&&A.every(acc=>acc.some(a=>words.includes(N(a))));});
    if(!ok)return;
    const slots=[...card.querySelectorAll('li.q input')];
    if(!slots.length)return;
    wire(bank,slots,UA?'Перетягни слово в пропуск або натисни на слово, а потім на пропуск.':'Drag a word into a gap, or tap a word and then a gap.');
  });
})();
