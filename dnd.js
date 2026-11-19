// Word bank: sticky bank for every exercise with a bank, plus drag-and-drop / tap-to-place
// for gap-fill exercises whose answers are bank words used as they are.
(function(){
  if(typeof SECS==='undefined')return;
  const css=`
.bank.sticky{position:sticky;top:0;z-index:5;background:var(--paper,#fff);margin:10px -22px 6px;padding:10px 22px;border-bottom:1px solid transparent;transition:box-shadow .15s,border-color .15s}
.bank.sticky.stuck{box-shadow:0 6px 12px -8px rgba(0,0,0,.25);border-color:var(--line,#eee)}
.bank.dnd span{cursor:grab;user-select:none;-webkit-user-select:none;touch-action:none;padding:5px 14px 4px 10px;
  background:linear-gradient(#FFF6D6,#F6E39E);border:1px solid #E2C55A;border-bottom:3px solid #C9A93E;
  box-shadow:0 2px 5px rgba(91,74,18,.18);transition:opacity .15s,transform .1s,box-shadow .1s}
.bank.dnd span::before{content:'⋮⋮';letter-spacing:-3px;margin-right:7px;opacity:.45;font-weight:700}
.bank.dnd span:hover{transform:translateY(-2px);box-shadow:0 5px 10px rgba(91,74,18,.22)}
.bank.dnd span:active{transform:translateY(1px);border-bottom-width:1px;margin-top:2px;box-shadow:0 1px 2px rgba(91,74,18,.2);cursor:grabbing}
.bank.dnd span.sel{outline:2.5px solid #22304A;outline-offset:2px}
.bank.dnd span.used{opacity:.4;box-shadow:none;border-bottom-width:1px;margin-top:2px;background:#FBF3D8}
.bank-tip{font-size:13px;color:#8a7f70;margin:-2px 0 6px}
li.q input.slot{cursor:pointer;caret-color:transparent;text-align:center;width:130px;height:34px;box-sizing:border-box;padding:3px 14px;margin:2px 4px;
  border-radius:999px;border:2px dashed #CDBF9F;background:#FFFDF6;font-weight:600;font-size:14px;color:#5B4A12;vertical-align:middle}
li.q input.slot.filled{border:1px solid #E2C55A;border-bottom:3px solid #C9A93E;background:linear-gradient(#FFF6D6,#F6E39E);box-shadow:0 2px 5px rgba(91,74,18,.18)}
li.q input.slot.over,li.q input.slot.target{border-color:#22304A;background:#F4F7FC}
li.q input.slot.over{transform:scale(1.06)}
li.q input.slot.ok1{border:2px solid var(--green,#2e8b57);background:#effaf4;box-shadow:none;color:inherit}
li.q input.slot.bad1{border:2px solid var(--red,#c0392b);background:#fff1f1;box-shadow:none;color:inherit}
li.q.bad input.slot.bad1:placeholder-shown{border-style:dashed}
.dnd-ghost{position:fixed;z-index:1000;pointer-events:none;background:linear-gradient(#FFF6D6,#F6E39E);border:1px solid #E2C55A;border-bottom:3px solid #C9A93E;color:#5B4A12;border-radius:999px;padding:5px 14px 4px;font:600 14px var(--sans,sans-serif);box-shadow:0 10px 22px rgba(0,0,0,.25);transform:translate(-50%,-60%) rotate(-3deg)}
`;
  const st=document.createElement('style');st.textContent=css;document.head.append(st);
  const N=typeof norm==='function'?norm:(s=>s.toLowerCase().trim());
  const cards=document.getElementById('secs').children;
  SECS.forEach((sec,si)=>{
    if(!sec.bank)return;const card=cards[si];if(!card)return;
    const bank=card.querySelector('.bank');if(!bank)return;
    bank.classList.add('sticky');
    // sticky shadow only while it is actually stuck
    const sentinel=document.createElement('div');bank.before(sentinel);
    new IntersectionObserver(([e])=>bank.classList.toggle('stuck',!e.isIntersecting&&e.boundingClientRect.top<0)).observe(sentinel);
    if(sec.type==='match'||sec.type==='choice'||sec.type==='order')return;
    const words=sec.bank.map(N);
    const ok=sec.items.every(it=>Array.isArray(it.a)&&it.a.every(acc=>acc.some(a=>words.includes(N(a)))));
    if(!ok)return;
    const slots=[...card.querySelectorAll('li.q input')];
    if(!slots.length)return;
    bank.classList.add('dnd');
    const tip=document.createElement('p');tip.className='bank-tip';
    tip.textContent=(typeof WHY_LANG!=='undefined'&&WHY_LANG!=='en')?'Перетягни слово в пропуск або натисни на слово, а потім на пропуск.':'Drag a word into a gap, or tap a word and then a gap.';
    bank.after(tip);
    const chips=[...bank.querySelectorAll('span')];
    let picked=null;
    const done=inp=>!!inp.closest('li.q').dataset.done;
    const refresh=()=>{const used={};slots.forEach(s=>{s.classList.toggle('filled',!!s.value);if(s.value)used[s.value]=(used[s.value]||0)+1;});
      chips.forEach(c=>{const w=c.textContent;c.classList.toggle('used',!!used[w]);});};
    const place=(inp,w)=>{if(done(inp))return;inp.value=w;refresh();};
    const unpick=()=>{if(picked)picked.classList.remove('sel');picked=null;slots.forEach(s=>s.classList.remove('target'));};
    slots.forEach(s=>{
      s.readOnly=true;s.classList.add('slot');s.setAttribute('inputmode','none');s.placeholder='';
      s.addEventListener('click',()=>{if(done(s))return;
        if(picked){place(s,picked.textContent);unpick();}
        else if(s.value){s.value='';refresh();}});
    });
    chips.forEach(c=>{
      c.addEventListener('pointerdown',e=>{
        if(e.button>0)return;e.preventDefault();
        const x0=e.clientX,y0=e.clientY;let ghost=null,over=null;
        const move=ev=>{
          if(!ghost&&Math.hypot(ev.clientX-x0,ev.clientY-y0)>6){ghost=document.createElement('div');ghost.className='dnd-ghost';ghost.textContent=c.textContent;document.body.append(ghost);unpick();}
          if(!ghost)return;ghost.style.left=ev.clientX+'px';ghost.style.top=ev.clientY+'px';
          const el=document.elementFromPoint(ev.clientX,ev.clientY);const t=el&&slots.includes(el)&&!done(el)?el:null;
          if(t!==over){over&&over.classList.remove('over');over=t;over&&over.classList.add('over');}
          // scroll the page while dragging near the window edge
          if(ev.clientY>innerHeight-50)scrollBy(0,14);else if(ev.clientY<50)scrollBy(0,-14);
        };
        const up=()=>{removeEventListener('pointermove',move);removeEventListener('pointerup',up);removeEventListener('pointercancel',up);
          if(ghost){ghost.remove();if(over){over.classList.remove('over');place(over,c.textContent);}}
          else{const was=picked===c;unpick();if(!was){picked=c;c.classList.add('sel');slots.forEach(s=>{if(!done(s))s.classList.add('target');});}}
        };
        addEventListener('pointermove',move);addEventListener('pointerup',up);addEventListener('pointercancel',up);
      });
    });
    const again=document.getElementById('again');if(again)again.addEventListener('click',()=>{unpick();refresh();});
    const check=document.getElementById('check');if(check)check.addEventListener('click',unpick);
  });
})();
