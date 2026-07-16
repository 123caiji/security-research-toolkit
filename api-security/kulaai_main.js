const __vite__mapDeps=(i,m=__vite__mapDeps,d=(m.f||(m.f=["assets/page-BV-cLHa8.js","assets/vendor-CmxBENpC.js","assets/rolldown-runtime-COnpUsM8.js","assets/vendor-7LyQelc0.css","assets/Countdown-6sBXXC32.js","assets/HtmlPreview-DIjdH5d-.js","assets/ThemeSwitch-D6b4EXNx.js","assets/api-B0xuzE-o.js","assets/auth-DuMKQslb.js","assets/storage-D66QG9aH.js","assets/SEO-DIVR8cmJ.js","assets/page-DQYTx3-_.js","assets/page-CUhktpCV.js","assets/page-Cg-SMgJi.js","assets/page-Cnm5dfWg.js","assets/page-CdVDJWlX.js","assets/page-B5yZ0BqV.js","assets/page-M6-UOEJj.js","assets/page-DJ_KFirf.js","assets/page-DcoFF2I1.js","assets/square-C3LlLvwm.js","assets/page-_4e3AbXN.js","assets/page-BqTy5xl5.js","assets/tag-DtxqVX68.js","assets/news-CEYk7MLf.js","assets/page-DA9ndLYC.js","assets/page-BDhjbMeJ.js","assets/page-DTQf2uI8.js","assets/page-CI2rFovR.js","assets/page-BT2RIqxS.js","assets/page-fzkb2HJA.js","assets/page-CI48SGlV.js","assets/page-DEZ5Uxjr.js"])))=>i.map(i=>d[i]);
import{a as e}from"./rolldown-runtime-COnpUsM8.js";import{$ as t,C as n,Ci as r,Cn as i,Di as a,E as o,Ei as s,Fi as c,Fr as l,Gr as u,In as d,It as f,J as ee,Jn as te,K as ne,L as p,M as re,Mi as m,Mt as h,Ni as g,Oi as ie,P as _,Pn as ae,Q as oe,S as se,Si as v,T as y,Ti as b,Wr as ce,X as le,Y as ue,Yt as x,Z as de,Zt as fe,_t as pe,ci as S,cn as me,ct as he,gn as ge,hi as _e,ii as C,mr as ve,nt as w,oi as T,q as ye,qn as E,st as be,un as xe,w as D,xi as Se,xt as O,yi as Ce,z as k}from"./vendor-CmxBENpC.js";import{r as A,t as j}from"./storage-D66QG9aH.js";import{_ as M,a as we,c as Te,i as Ee,l as N,o as De,r as Oe,s as ke,u as Ae}from"./auth-DuMKQslb.js";(function(){let e=document.createElement(`link`).relList;if(e&&e.supports&&e.supports(`modulepreload`))return;for(let e of document.querySelectorAll(`link[rel="modulepreload"]`))n(e);new MutationObserver(e=>{for(let t of e)if(t.type===`childList`)for(let e of t.addedNodes)e.tagName===`LINK`&&e.rel===`modulepreload`&&n(e)}).observe(document,{childList:!0,subtree:!0});function t(e){let t={};return e.integrity&&(t.integrity=e.integrity),e.referrerPolicy&&(t.referrerPolicy=e.referrerPolicy),e.crossOrigin===`use-credentials`?t.credentials=`include`:e.crossOrigin===`anonymous`?t.credentials=`omit`:t.credentials=`same-origin`,t}function n(e){if(e.ep)return;e.ep=!0;let n=t(e);fetch(e.href,n)}})();var P=g(),F=e(c(),1),I=Ce(),L=(0,F.createContext)({theme:`system`,resolvedTheme:`dark`,setTheme:()=>{}});function je(){return(0,F.useContext)(L)}function Me(){return typeof window>`u`||window.matchMedia(`(prefers-color-scheme: dark)`).matches?`dark`:`light`}function Ne({children:e}){let[t,n]=(0,F.useState)(`system`),[r,i]=(0,F.useState)(`dark`),[a,o]=(0,F.useState)(!1);return(0,F.useEffect)(()=>{let e=j(`theme`);e&&[`system`,`dark`,`light`].includes(e)?n(e):(A(`theme`,`system`),n(`system`)),o(!0)},[]),(0,F.useEffect)(()=>{if(!a)return;let e=t===`system`?Me():t;i(e);let n=document.documentElement;n.classList.remove(`light`,`dark`),n.classList.add(e)},[t,a]),(0,F.useEffect)(()=>{if(!a||t!==`system`)return;let e=window.matchMedia(`(prefers-color-scheme: dark)`),n=e=>{let t=e.matches?`dark`:`light`;i(t);let n=document.documentElement;n.classList.remove(`light`,`dark`),n.classList.add(t)};return e.addEventListener(`change`,n),()=>e.removeEventListener(`change`,n)},[t,a]),a?(0,I.jsx)(L.Provider,{value:{theme:t,resolvedTheme:r,setTheme:e=>{n(e),A(`theme`,e)}},children:e}):(0,I.jsx)(I.Fragment,{children:e})}var R=(0,F.createContext)({toast:()=>{}}),z={success:ce,error:u,info:E,warning:O},B={success:`border-green-500/30 bg-green-500/10 text-green-400`,error:`border-red-500/30 bg-red-500/10 text-red-400`,info:`border-blue-500/30 bg-blue-500/10 text-blue-400`,warning:`border-amber-500/30 bg-amber-500/10 text-amber-400`},V=0;function H({children:e}){let[t,n]=(0,F.useState)([]),r=(0,F.useCallback)((e,t=`info`)=>{let r=++V;n(n=>[...n,{id:r,message:e,type:t}]),setTimeout(()=>n(e=>e.filter(e=>e.id!==r)),3500)},[]),i=(0,F.useCallback)(e=>{n(t=>t.filter(t=>t.id!==e))},[]);return(0,F.useEffect)(()=>{let e=e=>{let{message:t,type:n}=e.detail||{};t&&r(t,n||`info`)};return window.addEventListener(`kulaai:toast`,e),()=>window.removeEventListener(`kulaai:toast`,e)},[r]),(0,I.jsxs)(R.Provider,{value:{toast:r},children:[e,t.length>0&&(0,I.jsx)(`div`,{className:`fixed top-4 right-4 z-[80] flex flex-col gap-2 max-w-sm`,children:t.map(e=>{let t=z[e.type];return(0,I.jsxs)(`div`,{className:`flex items-start gap-2.5 px-4 py-3 rounded-xl border backdrop-blur-xl shadow-lg animate-slide-in-right ${B[e.type]}`,children:[(0,I.jsx)(t,{size:16,className:`shrink-0 mt-0.5`}),(0,I.jsx)(`span`,{className:`text-sm flex-1 text-foreground`,children:e.message}),(0,I.jsx)(`button`,{onClick:()=>i(e.id),className:`shrink-0 p-0.5 rounded text-foreground/30 hover:text-foreground/60`,children:(0,I.jsx)(he,{size:12})})]},e.id)})})]})}function U(e,t=`info`){window.dispatchEvent(new CustomEvent(`kulaai:toast`,{detail:{message:e,type:t}}))}function W({children:e}){return(0,I.jsx)(w,{children:e})}var G=class extends F.Component{constructor(...e){super(...e),v(this,`state`,{hasError:!1,error:null})}static getDerivedStateFromError(e){return{hasError:!0,error:e}}componentDidCatch(e){if(e.message?.includes(`Failed to fetch dynamically imported module`)||e.message?.includes(`Loading chunk`)||e.message?.includes(`Loading CSS chunk`)){let e=`chunk_reload_ts`,t=Number(sessionStorage.getItem(e)||0);if(Date.now()-t>1e4){sessionStorage.setItem(e,String(Date.now())),window.location.reload();return}}}render(){return this.state.hasError?(0,I.jsx)(`div`,{className:`min-h-screen bg-background text-foreground flex items-center justify-center`,children:(0,I.jsxs)(`div`,{className:`text-center space-y-4 px-6`,children:[(0,I.jsx)(`div`,{className:`text-4xl`,children:`😵`}),(0,I.jsx)(`h2`,{className:`text-lg font-semibold`,children:`页面加载出错`}),(0,I.jsx)(`p`,{className:`text-sm text-accent max-w-xs mx-auto`,children:`可能是网络问题或版本更新导致，请刷新重试`}),(0,I.jsxs)(`button`,{onClick:()=>window.location.reload(),className:`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-foreground text-background text-sm font-medium hover:opacity-90 transition-colors`,children:[(0,I.jsx)(fe,{size:14}),`刷新页面`]})]})}):this.props.children}};function K({open:e,onClose:n,defaultTab:r=`login`,onSuccess:a,siteName:o=`KULAAI`,siteIcon:s}){let[c,l]=(0,F.useState)(r),[u,te]=(0,F.useState)(`phone-code`),[p,re]=(0,F.useState)(``),[m,h]=(0,F.useState)(``),[g,ie]=(0,F.useState)(``),[_,se]=(0,F.useState)(``),[v,y]=(0,F.useState)(``),[b,ce]=(0,F.useState)(`email`),[x,fe]=(0,F.useState)(``),[S,_e]=(0,F.useState)(``),[C,ve]=(0,F.useState)(``),[w,T]=(0,F.useState)(``),[E,xe]=(0,F.useState)(``),[D,Se]=(0,F.useState)(`email`),[O,Ce]=(0,F.useState)(``),[k,A]=(0,F.useState)(``),[M,P]=(0,F.useState)(``),[L,je]=(0,F.useState)(``),[Me,Ne]=(0,F.useState)(!1),[R,z]=(0,F.useState)(``),[B,V]=(0,F.useState)(!1),[H,U]=(0,F.useState)(!1),[W,G]=(0,F.useState)(0),[K,q]=(0,F.useState)(null),[J,Pe]=(0,F.useState)(!1);(0,F.useEffect)(()=>{e&&(l(r),z(``),Oe().then(e=>Pe(e.smsEnabled)))},[e,r]),(0,F.useEffect)(()=>{if(W<=0)return;let e=setTimeout(()=>G(W-1),1e3);return()=>clearTimeout(e)},[W]);let Fe=()=>{z(``),y(``),T(``),G(0)},Y=e=>{l(e),Fe(),Ne(!1),P(``),je(``)},X=e=>{e!==u&&(te(e),y(``),G(0),z(``))},Ie=(0,F.useCallback)(async()=>{if(z(``),u===`email-code`){if(!m){z(`请输入邮箱`);return}U(!0);try{await N(m),G(60)}catch(e){z(e.message||`发送验证码失败`)}finally{U(!1)}}else if(u===`phone-code`){if(!g){z(`请输入手机号`);return}if(!/^1[3-9]\d{9}$/.test(g)){z(`手机号格式不正确`);return}U(!0);try{await Ae(g),G(60)}catch(e){z(e.message||`发送验证码失败`)}finally{U(!1)}}},[u,m,g]),Le=async e=>{e.preventDefault(),z(``),V(!0);try{let e=j(`kulaai_agent_ref`)||void 0;u===`email-code`?await Ee({email:m,code:v,inviteCode:e}):u===`phone-code`?await we({phone:g,code:v,inviteCode:e}):await Ee(/^1[3-9]\d{9}$/.test(p)?{phone:p,password:_,inviteCode:e}:{email:p,password:_,inviteCode:e}),a?.(),n(),window.location.reload()}catch(e){z(e.message||`登录失败`)}finally{V(!1)}},Re=e=>{e!==b&&(ce(e),T(``),G(0),z(``))},ze=(0,F.useCallback)(async()=>{if(z(``),b===`email`){if(!x){z(`请输入邮箱`);return}U(!0);try{await N(x),G(60)}catch(e){z(e.message||`发送验证码失败`)}finally{U(!1)}}else{if(!S){z(`请输入手机号`);return}if(!/^1[3-9]\d{9}$/.test(S)){z(`手机号格式不正确`);return}U(!0);try{await Ae(S),G(60)}catch(e){z(e.message||`发送验证码失败`)}finally{U(!1)}}},[b,x,S]),Be=async e=>{if(e.preventDefault(),z(``),C.length<6){z(`密码至少6位`);return}if(!w){z(`请输入验证码`);return}V(!0);try{let e=j(`kulaai_agent_ref`)||void 0;b===`email`?await De({email:x,password:C,code:w,nickname:E||void 0,inviteCode:e}):await ke({phone:S,password:C,code:w,nickname:E||void 0,inviteCode:e}),a?.(),n(),window.location.reload()}catch(e){z(e.message||`注册失败`)}finally{V(!1)}};if(!e)return null;let Z=[{icon:(0,I.jsx)(be,{size:16}),text:`多模型 AI 智能对话`},{icon:(0,I.jsx)(ge,{size:16}),text:`AI 绘图 / 视频 / 音频`},{icon:(0,I.jsx)(i,{size:16}),text:`多平台多尺寸适配`},{icon:(0,I.jsx)(f,{size:16}),text:`安全稳定，开箱即用`}],Q=e=>`relative rounded-xl border transition-all duration-200 ${K===e?`border-orange-400/50 bg-orange-50/5`:`border-foreground/[0.08] bg-foreground/[0.02]`}`,$=e=>`absolute left-4 top-1/2 -translate-y-1/2 transition-colors duration-200 ${K===e?`text-orange-400`:`text-accent/50`}`;return(0,I.jsx)(`div`,{className:`fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm`,onClick:n,children:(0,I.jsxs)(`div`,{className:`relative w-full max-w-[780px] mx-4 bg-background border border-foreground/[0.08] rounded-2xl shadow-2xl overflow-hidden flex`,onClick:e=>e.stopPropagation(),children:[(0,I.jsxs)(`div`,{className:`hidden md:flex w-[280px] shrink-0 flex-col justify-between p-7 rounded-l-2xl`,style:{background:`linear-gradient(135deg, #3a3a3a, #6b6b6b, #9ca3af)`},children:[(0,I.jsxs)(`div`,{children:[(0,I.jsxs)(`div`,{className:`flex items-center gap-2.5 mb-8`,children:[s?(0,I.jsx)(`img`,{src:s,alt:``,className:`w-9 h-9 rounded-xl object-contain`}):(0,I.jsx)(`div`,{className:`w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center`,children:(0,I.jsx)(`span`,{className:`text-white text-sm font-black`,children:`AI+`})}),(0,I.jsxs)(`div`,{children:[(0,I.jsx)(`div`,{className:`text-white font-bold text-sm`,children:o}),(0,I.jsx)(`div`,{className:`text-white/60 text-[10px]`,children:`AI 智能助手`})]})]}),(0,I.jsxs)(`h2`,{className:`text-white font-extrabold text-xl leading-tight mb-2`,children:[`让 AI 赋能`,(0,I.jsx)(`br`,{}),`更简单高效`]}),(0,I.jsxs)(`p`,{className:`text-white/60 text-xs leading-relaxed mb-8`,children:[`登录后即可解锁全部功能，`,(0,I.jsx)(`br`,{}),`享受 AI 驱动的智能体验。`]}),(0,I.jsx)(`div`,{className:`space-y-3.5`,children:Z.map((e,t)=>(0,I.jsxs)(`div`,{className:`flex items-center gap-2.5`,children:[(0,I.jsx)(`span`,{className:`text-white/80`,children:e.icon}),(0,I.jsx)(`span`,{className:`text-white/90 text-xs font-medium`,children:e.text})]},t))}),(0,I.jsxs)(`div`,{className:`mt-8`,children:[(0,I.jsx)(`p`,{className:`text-white/40 text-[10px] font-semibold tracking-wider mb-3`,children:`支持主流大模型`}),(0,I.jsx)(`div`,{className:`grid grid-cols-4 gap-2`,children:[{icon:(0,I.jsx)(t,{size:16}),name:`GPT`},{icon:(0,I.jsx)(oe,{size:16}),name:`Claude`},{icon:(0,I.jsx)(de,{size:16}),name:`Gemini`},{icon:(0,I.jsx)(ne,{size:16}),name:`Grok`},{icon:(0,I.jsx)(le,{size:16}),name:`DeepSeek`},{icon:(0,I.jsx)(ue,{size:16}),name:`通义千问`},{icon:(0,I.jsx)(ee,{size:16}),name:`豆包`},{icon:(0,I.jsx)(ye,{size:16}),name:`Kimi`}].map((e,t)=>(0,I.jsxs)(`div`,{className:`flex flex-col items-center gap-1 py-1.5 rounded-lg bg-white/[0.06]`,children:[(0,I.jsx)(`span`,{className:`text-white/70`,children:e.icon}),(0,I.jsx)(`span`,{className:`text-white/50 text-[9px] leading-none`,children:e.name})]},t))})]})]}),(0,I.jsxs)(`p`,{className:`text-white/30 text-[10px]`,children:[`© `,new Date().getFullYear(),` `,o,` 保留所有权利`]})]}),(0,I.jsxs)(`div`,{className:`flex-1 flex flex-col min-w-0`,children:[(0,I.jsx)(`button`,{onClick:n,className:`absolute top-4 right-4 z-10 p-1.5 rounded-lg text-accent hover:text-foreground hover:bg-foreground/5 transition-colors`,children:(0,I.jsx)(he,{size:18})}),(0,I.jsx)(`div`,{className:`flex-1 px-7 py-8 overflow-y-auto max-h-[85vh]`,children:c===`login`?(0,I.jsxs)(I.Fragment,{children:[(0,I.jsx)(`h2`,{className:`text-xl font-bold text-foreground mb-1`,children:`欢迎登录`}),(0,I.jsx)(`p`,{className:`text-xs text-foreground/40 mb-6`,children:u===`phone-code`?`手机验证码快速登录 / 注册`:u===`email-code`?`邮箱验证码快速登录`:`使用账号密码登录`}),(0,I.jsxs)(`form`,{onSubmit:Le,className:`space-y-3.5`,children:[R&&(0,I.jsxs)(`div`,{className:`px-4 py-2.5 rounded-xl bg-red-500/[0.08] border border-red-500/15 text-red-400 text-sm flex items-center gap-2`,children:[(0,I.jsx)(`div`,{className:`w-1.5 h-1.5 rounded-full bg-red-400 shrink-0`}),R]}),u===`phone-code`?(0,I.jsxs)(`div`,{className:Q(`l-phone`),children:[(0,I.jsxs)(`div`,{className:`absolute left-4 top-1/2 -translate-y-1/2 flex items-center gap-1.5 text-foreground/50 text-sm pointer-events-none`,children:[(0,I.jsx)(me,{size:14}),(0,I.jsx)(`span`,{className:`text-xs`,children:`+86`}),(0,I.jsx)(`span`,{className:`text-foreground/15`,children:`|`})]}),(0,I.jsx)(`input`,{type:`tel`,value:g,onChange:e=>ie(e.target.value),onFocus:()=>q(`l-phone`),onBlur:()=>q(null),placeholder:`请输入手机号`,required:!0,maxLength:11,className:`w-full bg-transparent rounded-xl pl-[88px] pr-4 py-3.5 text-sm text-foreground placeholder-accent/30 outline-none`})]}):u===`email-code`?(0,I.jsxs)(`div`,{className:Q(`l-email`),children:[(0,I.jsx)(ae,{size:16,className:$(`l-email`)}),(0,I.jsx)(`input`,{type:`email`,value:m,onChange:e=>h(e.target.value),onFocus:()=>q(`l-email`),onBlur:()=>q(null),placeholder:`请输入邮箱地址`,required:!0,className:`w-full bg-transparent rounded-xl pl-10 pr-4 py-3.5 text-sm text-foreground placeholder-accent/30 outline-none`})]}):(0,I.jsxs)(`div`,{className:Q(`l-account`),children:[(0,I.jsx)(pe,{size:16,className:$(`l-account`)}),(0,I.jsx)(`input`,{type:`text`,value:p,onChange:e=>re(e.target.value),onFocus:()=>q(`l-account`),onBlur:()=>q(null),placeholder:`邮箱或手机号`,required:!0,className:`w-full bg-transparent rounded-xl pl-10 pr-4 py-3.5 text-sm text-foreground placeholder-accent/30 outline-none`})]}),u===`password`?(0,I.jsxs)(`div`,{className:Q(`l-password`),children:[(0,I.jsx)(d,{size:16,className:$(`l-password`)}),(0,I.jsx)(`input`,{type:`password`,value:_,onChange:e=>se(e.target.value),onFocus:()=>q(`l-password`),onBlur:()=>q(null),placeholder:`请输入密码`,required:!0,className:`w-full bg-transparent rounded-xl pl-10 pr-4 py-3.5 text-sm text-foreground placeholder-accent/30 outline-none`})]}):(0,I.jsx)(I.Fragment,{children:(0,I.jsxs)(`div`,{className:`flex gap-2`,children:[(0,I.jsxs)(`div`,{className:`flex-1 ${Q(`l-code`)}`,children:[(0,I.jsx)(f,{size:16,className:$(`l-code`)}),(0,I.jsx)(`input`,{type:`text`,value:v,onChange:e=>y(e.target.value),onFocus:()=>q(`l-code`),onBlur:()=>q(null),placeholder:`请输入短信验证码`,required:!0,maxLength:6,className:`w-full bg-transparent rounded-xl pl-10 pr-4 py-3.5 text-sm text-foreground placeholder-accent/30 outline-none tracking-widest`})]}),(0,I.jsx)(`button`,{type:`button`,onClick:Ie,disabled:H||W>0,className:`px-4 rounded-xl border border-orange-400/40 text-orange-400 text-xs font-medium hover:bg-orange-400/10 transition-all disabled:opacity-40 whitespace-nowrap shrink-0`,children:W>0?`${W}s`:H?`...`:`获取验证码`})]})}),(0,I.jsx)(`button`,{type:`submit`,disabled:B||u!==`password`&&!v.trim(),className:`w-full py-3.5 rounded-xl font-semibold text-sm text-white transition-all flex items-center justify-center gap-2 ${u!==`password`&&!v.trim()?`opacity-40 cursor-not-allowed`:``}`,style:{background:u!==`password`&&!v.trim()?`#555`:`linear-gradient(135deg, #ff6b35, #f7931e)`},children:B?(0,I.jsxs)(`span`,{className:`flex items-center gap-2`,children:[(0,I.jsx)(`div`,{className:`w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin`}),`登录中...`]}):u===`password`?`登录`:`登录 / 注册`}),u===`password`&&(0,I.jsxs)(`div`,{className:`flex items-center justify-between mt-2`,children:[(0,I.jsx)(`p`,{className:`text-[11px] text-foreground/30`,children:`请先通过验证码注册后再用密码登录`}),(0,I.jsx)(`button`,{type:`button`,onClick:()=>Y(`forgot`),className:`text-[11px] text-orange-400/70 hover:text-orange-400 transition-colors shrink-0 ml-2`,children:`忘记密码?`})]})]}),(0,I.jsxs)(`p`,{className:`text-center text-[11px] text-foreground/30 mt-3`,children:[`登录即同意 `,(0,I.jsx)(`a`,{href:`/terms`,target:`_blank`,className:`text-orange-400/70 hover:text-orange-400`,children:`用户协议`}),` 和 `,(0,I.jsx)(`a`,{href:`/privacy`,target:`_blank`,className:`text-orange-400/70 hover:text-orange-400`,children:`隐私政策`})]}),(0,I.jsxs)(`div`,{className:`flex items-center gap-3 my-5`,children:[(0,I.jsx)(`div`,{className:`flex-1 h-px bg-foreground/[0.06]`}),(0,I.jsx)(`span`,{className:`text-[11px] text-foreground/25`,children:`或`}),(0,I.jsx)(`div`,{className:`flex-1 h-px bg-foreground/[0.06]`})]}),(0,I.jsxs)(`div`,{className:`flex flex-col gap-2`,children:[u!==`password`&&(0,I.jsx)(`button`,{type:`button`,onClick:()=>X(`password`),className:`w-full py-3 rounded-xl border border-foreground/[0.08] text-foreground/60 text-sm font-medium hover:bg-foreground/[0.03] hover:border-foreground/15 transition-all`,children:`密码登录`}),u!==`email-code`&&(0,I.jsx)(`button`,{type:`button`,onClick:()=>X(`email-code`),className:`w-full py-3 rounded-xl border border-foreground/[0.08] text-foreground/60 text-sm font-medium hover:bg-foreground/[0.03] hover:border-foreground/15 transition-all`,children:`邮箱验证码登录`}),J&&u!==`phone-code`&&(0,I.jsx)(`button`,{type:`button`,onClick:()=>X(`phone-code`),className:`w-full py-3 rounded-xl border border-foreground/[0.08] text-foreground/60 text-sm font-medium hover:bg-foreground/[0.03] hover:border-foreground/15 transition-all`,children:`手机验证码登录`})]})]}):c===`register`?(0,I.jsxs)(I.Fragment,{children:[(0,I.jsx)(`h2`,{className:`text-xl font-bold text-foreground mb-1`,children:`创建账号`}),(0,I.jsx)(`p`,{className:`text-xs text-foreground/40 mb-6`,children:b===`phone`?`使用手机号注册新账号`:`使用邮箱注册新账号`}),J&&(0,I.jsxs)(`div`,{className:`flex mb-4 p-1 rounded-xl bg-foreground/[0.03] border border-foreground/[0.05]`,children:[(0,I.jsx)(`button`,{type:`button`,onClick:()=>Re(`email`),className:`flex-1 py-2 rounded-lg text-xs font-medium transition-all ${b===`email`?`bg-foreground/10 text-foreground`:`text-accent hover:text-foreground`}`,children:`邮箱注册`}),(0,I.jsx)(`button`,{type:`button`,onClick:()=>Re(`phone`),className:`flex-1 py-2 rounded-lg text-xs font-medium transition-all ${b===`phone`?`bg-foreground/10 text-foreground`:`text-accent hover:text-foreground`}`,children:`手机号注册`})]}),(0,I.jsxs)(`form`,{onSubmit:Be,className:`space-y-3.5`,children:[R&&(0,I.jsxs)(`div`,{className:`px-4 py-2.5 rounded-xl bg-red-500/[0.08] border border-red-500/15 text-red-400 text-sm flex items-center gap-2`,children:[(0,I.jsx)(`div`,{className:`w-1.5 h-1.5 rounded-full bg-red-400 shrink-0`}),R]}),b===`email`?(0,I.jsxs)(`div`,{className:Q(`r-email`),children:[(0,I.jsx)(ae,{size:16,className:$(`r-email`)}),(0,I.jsx)(`input`,{type:`email`,value:x,onChange:e=>fe(e.target.value),onFocus:()=>q(`r-email`),onBlur:()=>q(null),placeholder:`请输入邮箱地址`,required:!0,className:`w-full bg-transparent rounded-xl pl-10 pr-4 py-3.5 text-sm text-foreground placeholder-accent/30 outline-none`})]}):(0,I.jsxs)(`div`,{className:Q(`r-phone`),children:[(0,I.jsxs)(`div`,{className:`absolute left-4 top-1/2 -translate-y-1/2 flex items-center gap-1.5 text-foreground/50 text-sm pointer-events-none`,children:[(0,I.jsx)(me,{size:14}),(0,I.jsx)(`span`,{className:`text-xs`,children:`+86`}),(0,I.jsx)(`span`,{className:`text-foreground/15`,children:`|`})]}),(0,I.jsx)(`input`,{type:`tel`,value:S,onChange:e=>_e(e.target.value),onFocus:()=>q(`r-phone`),onBlur:()=>q(null),placeholder:`请输入手机号`,required:!0,maxLength:11,className:`w-full bg-transparent rounded-xl pl-[88px] pr-4 py-3.5 text-sm text-foreground placeholder-accent/30 outline-none`})]}),(0,I.jsxs)(`div`,{className:`flex gap-2`,children:[(0,I.jsxs)(`div`,{className:`flex-1 ${Q(`r-code`)}`,children:[(0,I.jsx)(f,{size:16,className:$(`r-code`)}),(0,I.jsx)(`input`,{type:`text`,value:w,onChange:e=>T(e.target.value),onFocus:()=>q(`r-code`),onBlur:()=>q(null),placeholder:`请输入验证码`,required:!0,maxLength:6,className:`w-full bg-transparent rounded-xl pl-10 pr-4 py-3.5 text-sm text-foreground placeholder-accent/30 outline-none tracking-widest`})]}),(0,I.jsx)(`button`,{type:`button`,onClick:ze,disabled:H||W>0,className:`px-4 rounded-xl border border-orange-400/40 text-orange-400 text-xs font-medium hover:bg-orange-400/10 transition-all disabled:opacity-40 whitespace-nowrap shrink-0`,children:W>0?`${W}s`:H?`...`:`获取验证码`})]}),(0,I.jsxs)(`div`,{className:Q(`r-nickname`),children:[(0,I.jsx)(pe,{size:16,className:$(`r-nickname`)}),(0,I.jsx)(`input`,{type:`text`,value:E,onChange:e=>xe(e.target.value),onFocus:()=>q(`r-nickname`),onBlur:()=>q(null),placeholder:`昵称（可选）`,className:`w-full bg-transparent rounded-xl pl-10 pr-4 py-3.5 text-sm text-foreground placeholder-accent/30 outline-none`})]}),(0,I.jsxs)(`div`,{className:Q(`r-password`),children:[(0,I.jsx)(d,{size:16,className:$(`r-password`)}),(0,I.jsx)(`input`,{type:`password`,value:C,onChange:e=>ve(e.target.value),onFocus:()=>q(`r-password`),onBlur:()=>q(null),placeholder:`密码（至少6位）`,required:!0,minLength:6,className:`w-full bg-transparent rounded-xl pl-10 pr-4 py-3.5 text-sm text-foreground placeholder-accent/30 outline-none`})]}),(0,I.jsx)(`button`,{type:`submit`,disabled:B||!w.trim(),className:`w-full py-3.5 rounded-xl font-semibold text-sm text-white transition-all flex items-center justify-center gap-2 ${w.trim()?``:`opacity-40 cursor-not-allowed`}`,style:{background:w.trim()?`linear-gradient(135deg, #ff6b35, #f7931e)`:`#555`},children:B?(0,I.jsxs)(`span`,{className:`flex items-center gap-2`,children:[(0,I.jsx)(`div`,{className:`w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin`}),`注册中...`]}):`注册`})]}),(0,I.jsxs)(`p`,{className:`text-center text-[11px] text-foreground/30 mt-3`,children:[`注册即同意 `,(0,I.jsx)(`a`,{href:`/terms`,target:`_blank`,className:`text-orange-400/70 hover:text-orange-400`,children:`用户协议`}),` 和 `,(0,I.jsx)(`a`,{href:`/privacy`,target:`_blank`,className:`text-orange-400/70 hover:text-orange-400`,children:`隐私政策`})]}),(0,I.jsxs)(`div`,{className:`flex items-center gap-3 my-5`,children:[(0,I.jsx)(`div`,{className:`flex-1 h-px bg-foreground/[0.06]`}),(0,I.jsx)(`span`,{className:`text-[11px] text-foreground/25`,children:`或`}),(0,I.jsx)(`div`,{className:`flex-1 h-px bg-foreground/[0.06]`})]}),(0,I.jsx)(`button`,{type:`button`,onClick:()=>Y(`login`),className:`w-full py-3 rounded-xl border border-foreground/[0.08] text-foreground/60 text-sm font-medium hover:bg-foreground/[0.03] hover:border-foreground/15 transition-all`,children:`已有账号？去登录`})]}):(0,I.jsxs)(I.Fragment,{children:[(0,I.jsx)(`h2`,{className:`text-xl font-bold text-foreground mb-1`,children:`重置密码`}),(0,I.jsx)(`p`,{className:`text-xs text-foreground/40 mb-6`,children:Me?`密码已重置成功，请使用新密码登录`:`通过验证码验证身份后设置新密码`}),Me?(0,I.jsx)(`button`,{type:`button`,onClick:()=>Y(`login`),className:`w-full py-3.5 rounded-xl font-semibold text-sm text-white flex items-center justify-center gap-2`,style:{background:`linear-gradient(135deg, #ff6b35, #f7931e)`},children:`返回登录`}):(0,I.jsxs)(I.Fragment,{children:[J&&(0,I.jsxs)(`div`,{className:`flex mb-4 p-1 rounded-xl bg-foreground/[0.03] border border-foreground/[0.05]`,children:[(0,I.jsx)(`button`,{type:`button`,onClick:()=>{Se(`email`),z(``),G(0),P(``)},className:`flex-1 py-2 rounded-lg text-xs font-medium transition-all ${D===`email`?`bg-foreground/10 text-foreground`:`text-accent hover:text-foreground`}`,children:`邮箱验证`}),(0,I.jsx)(`button`,{type:`button`,onClick:()=>{Se(`phone`),z(``),G(0),P(``)},className:`flex-1 py-2 rounded-lg text-xs font-medium transition-all ${D===`phone`?`bg-foreground/10 text-foreground`:`text-accent hover:text-foreground`}`,children:`手机验证`})]}),(0,I.jsxs)(`form`,{onSubmit:async e=>{if(e.preventDefault(),z(``),L.length<6){z(`密码至少6位`);return}if(!M){z(`请输入验证码`);return}V(!0);try{await Te({email:D===`email`?O:void 0,phone:D===`phone`?k:void 0,code:M,password:L}),Ne(!0)}catch(e){z(e.message||`重置密码失败`)}finally{V(!1)}},className:`space-y-3.5`,children:[R&&(0,I.jsxs)(`div`,{className:`px-4 py-2.5 rounded-xl bg-red-500/[0.08] border border-red-500/15 text-red-400 text-sm flex items-center gap-2`,children:[(0,I.jsx)(`div`,{className:`w-1.5 h-1.5 rounded-full bg-red-400 shrink-0`}),R]}),D===`email`?(0,I.jsxs)(`div`,{className:Q(`f-email`),children:[(0,I.jsx)(ae,{size:16,className:$(`f-email`)}),(0,I.jsx)(`input`,{type:`email`,value:O,onChange:e=>Ce(e.target.value),onFocus:()=>q(`f-email`),onBlur:()=>q(null),placeholder:`请输入注册邮箱`,required:!0,className:`w-full bg-transparent rounded-xl pl-10 pr-4 py-3.5 text-sm text-foreground placeholder-accent/30 outline-none`})]}):(0,I.jsxs)(`div`,{className:Q(`f-phone`),children:[(0,I.jsxs)(`div`,{className:`absolute left-4 top-1/2 -translate-y-1/2 flex items-center gap-1.5 text-foreground/50 text-sm pointer-events-none`,children:[(0,I.jsx)(me,{size:14}),(0,I.jsx)(`span`,{className:`text-xs`,children:`+86`}),(0,I.jsx)(`span`,{className:`text-foreground/15`,children:`|`})]}),(0,I.jsx)(`input`,{type:`tel`,value:k,onChange:e=>A(e.target.value),onFocus:()=>q(`f-phone`),onBlur:()=>q(null),placeholder:`请输入注册手机号`,required:!0,maxLength:11,className:`w-full bg-transparent rounded-xl pl-[88px] pr-4 py-3.5 text-sm text-foreground placeholder-accent/30 outline-none`})]}),(0,I.jsxs)(`div`,{className:`flex gap-2`,children:[(0,I.jsxs)(`div`,{className:`flex-1 ${Q(`f-code`)}`,children:[(0,I.jsx)(f,{size:16,className:$(`f-code`)}),(0,I.jsx)(`input`,{type:`text`,value:M,onChange:e=>P(e.target.value),onFocus:()=>q(`f-code`),onBlur:()=>q(null),placeholder:`请输入验证码`,required:!0,maxLength:6,className:`w-full bg-transparent rounded-xl pl-10 pr-4 py-3.5 text-sm text-foreground placeholder-accent/30 outline-none tracking-widest`})]}),(0,I.jsx)(`button`,{type:`button`,onClick:async()=>{z(``),U(!0);try{if(D===`email`){if(!O){z(`请输入邮箱`),U(!1);return}await N(O)}else{if(!k||!/^1[3-9]\d{9}$/.test(k)){z(`请输入正确的手机号`),U(!1);return}await Ae(k)}G(60)}catch(e){z(e.message||`发送验证码失败`)}finally{U(!1)}},disabled:H||W>0,className:`px-4 rounded-xl border border-orange-400/40 text-orange-400 text-xs font-medium hover:bg-orange-400/10 transition-all disabled:opacity-40 whitespace-nowrap shrink-0`,children:W>0?`${W}s`:H?`...`:`获取验证码`})]}),(0,I.jsxs)(`div`,{className:Q(`f-password`),children:[(0,I.jsx)(d,{size:16,className:$(`f-password`)}),(0,I.jsx)(`input`,{type:`password`,value:L,onChange:e=>je(e.target.value),onFocus:()=>q(`f-password`),onBlur:()=>q(null),placeholder:`设置新密码（至少6位）`,required:!0,minLength:6,className:`w-full bg-transparent rounded-xl pl-10 pr-4 py-3.5 text-sm text-foreground placeholder-accent/30 outline-none`})]}),(0,I.jsx)(`button`,{type:`submit`,disabled:B||!M.trim(),className:`w-full py-3.5 rounded-xl font-semibold text-sm text-white transition-all flex items-center justify-center gap-2 ${M.trim()?``:`opacity-40 cursor-not-allowed`}`,style:{background:M.trim()?`linear-gradient(135deg, #ff6b35, #f7931e)`:`#555`},children:B?(0,I.jsxs)(`span`,{className:`flex items-center gap-2`,children:[(0,I.jsx)(`div`,{className:`w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin`}),`重置中...`]}):`重置密码`})]}),(0,I.jsxs)(`div`,{className:`flex items-center gap-3 my-5`,children:[(0,I.jsx)(`div`,{className:`flex-1 h-px bg-foreground/[0.06]`}),(0,I.jsx)(`span`,{className:`text-[11px] text-foreground/25`,children:`或`}),(0,I.jsx)(`div`,{className:`flex-1 h-px bg-foreground/[0.06]`})]}),(0,I.jsx)(`button`,{type:`button`,onClick:()=>Y(`login`),className:`w-full py-3 rounded-xl border border-foreground/[0.08] text-foreground/60 text-sm font-medium hover:bg-foreground/[0.03] hover:border-foreground/15 transition-all`,children:`返回登录`})]})]})})]})]})})}var q=`/assets/hero-5sT3BiRD.png`,J=[1,2,3,4,5,6,7,8,9,10];function Pe(e){return J.includes(e)}function Fe(e=window.location.search){let t=new URLSearchParams(e),n=t.get(`template`)||t.get(`预览模板`);if(!n)return null;let r=Number.parseInt(n,10);return Pe(r)?r:null}function Y(e=window.location.search){return Fe(e)||J[Math.floor(Math.random()*J.length)]||1}var X=[{id:1,name:`深空智能中枢`,label:`AI Command Center`,headline:`把复杂任务交给一个发光的 AI 控制台`,subline:`对话、创作、搜索、文件理解和自动化流程集中在同一个登录前入口。`,icon:T,primary:`#00d4ff`,secondary:`#7c3aed`,accent:`#22c55e`,bg:`#030712`,text:`#f8fafc`,muted:`rgba(226,232,240,.74)`,panel:`rgba(8,13,29,.72)`,border:`rgba(0,212,255,.32)`,scene:`cyber`,features:[`多模型对话`,`知识检索`,`文件理解`],metrics:[{value:`20+`,label:`能力入口`},{value:`7x24`,label:`在线协作`},{value:`1`,label:`统一工作台`}],chips:[`GPT`,`Claude`,`DeepSeek`,`Gemini`]},{id:2,name:`霓虹创作者影棚`,label:`Creator Studio`,headline:`从一句想法开始，生成完整内容资产`,subline:`文案、图片、视频脚本和发布素材在一条高亮工作流里连续完成。`,icon:h,primary:`#ff2d80`,secondary:`#facc15`,accent:`#00ffe5`,bg:`#17051f`,text:`#fff7ed`,muted:`rgba(255,247,237,.76)`,panel:`rgba(59,7,42,.68)`,border:`rgba(255,45,128,.34)`,scene:`racing`,features:[`爆款文案`,`视觉生成`,`视频分镜`],metrics:[{value:`4`,label:`创作链路`},{value:`AI`,label:`灵感扩展`},{value:`HD`,label:`素材输出`}],chips:[`图文`,`短视频`,`脚本`,`配音`]},{id:3,name:`企业知识光舱`,label:`Knowledge Hub`,headline:`让资料、报告和决策在一个空间里流动`,subline:`上传文件后直接提问，快速整理重点、结论和下一步行动。`,icon:ve,primary:`#22c55e`,secondary:`#38bdf8`,accent:`#eab308`,bg:`#052e2b`,text:`#ecfdf5`,muted:`rgba(236,253,245,.74)`,panel:`rgba(6,78,59,.68)`,border:`rgba(52,211,153,.32)`,scene:`aurora`,features:[`文档总结`,`报告生成`,`资料问答`],metrics:[{value:`PDF`,label:`文件解析`},{value:`3步`,label:`形成报告`},{value:`0`,label:`重复整理`}],chips:[`合同`,`论文`,`表格`,`纪要`]},{id:4,name:`研发终端矩阵`,label:`Dev Copilot`,headline:`把研发问题拆成可执行的工程步骤`,subline:`从需求梳理、代码解释到调试建议，保持上下文连续。`,icon:l,primary:`#60a5fa`,secondary:`#c084fc`,accent:`#34d399`,bg:`#020617`,text:`#eff6ff`,muted:`rgba(239,246,255,.72)`,panel:`rgba(15,23,42,.72)`,border:`rgba(96,165,250,.34)`,scene:`terminal`,features:[`代码理解`,`方案推演`,`测试建议`],metrics:[{value:`API`,label:`接口协同`},{value:`PRD`,label:`需求拆解`},{value:`Bug`,label:`问题定位`}],chips:[`React`,`Node`,`SQL`,`Docker`]},{id:5,name:`极光白色入口`,label:`Minimal Workspace`,headline:`清爽进入 AI 工作区，直接处理今天的任务`,subline:`没有多余层级，登录后回到原本要访问的系统页面。`,icon:x,primary:`#2563eb`,secondary:`#06b6d4`,accent:`#111827`,bg:`#eef6ff`,text:`#f8fafc`,muted:`rgba(248,250,252,.78)`,panel:`rgba(255,255,255,.74)`,border:`rgba(37,99,235,.28)`,scene:`glass`,features:[`快速进入`,`任务连续`,`账号同步`],metrics:[{value:`1秒`,label:`启动入口`},{value:`10`,label:`模板随机`},{value:`100%`,label:`系统保留`}],chips:[`对话`,`创作`,`管理`,`订单`]},{id:6,name:`梦境生成器`,label:`Dream Studio`,headline:`梦境，由你造。`,subline:`用文字召唤画面，用想象生成视频。把每一束灵感，变成属于你的极光。`,icon:h,primary:`#d946ef`,secondary:`#7c3aed`,accent:`#60a5fa`,bg:`#08051a`,text:`#f8f7ff`,muted:`rgba(248,247,255,.72)`,panel:`rgba(24,16,48,.58)`,border:`rgba(217,70,239,.3)`,scene:`dream`,composition:`dream`,features:[`文字成片`,`灵感扩写`,`梦境渲染`],metrics:[{value:`500+`,label:`模型能力`},{value:`10K+`,label:`创作者`},{value:`∞`,label:`想象力`}],chips:[`omni-flash`,`Suno 音乐生成 4.5`,`Gemini 3.5 flash`,`grok-4.3`,`VIDU Image 2`,`快马-文生视频`]},{id:7,name:`金色模型画廊`,label:`Galleria AI`,headline:`AI 笔下的新文艺复兴`,subline:`每一帧都是一幅画作，每一次输出都值得镶进金边相框。`,icon:te,primary:`#caa64d`,secondary:`#8a5f1f`,accent:`#f4d48a`,bg:`#160802`,text:`#f8edd3`,muted:`rgba(248,237,211,.72)`,panel:`rgba(36,18,8,.7)`,border:`rgba(202,166,77,.42)`,scene:`gallery`,composition:`gallery`,features:[`画廊策展`,`图像生成`,`视频藏品`],metrics:[{value:`500+`,label:`馆藏`},{value:`120`,label:`在席`},{value:`∞`,label:`出品`}],chips:[`Gemini 3.5 flash`,`Suno`,`VIDU 音乐MV`,`grok-4.3`]},{id:8,name:`粉色灵感手账`,label:`Bloom Notes`,headline:`把每一个想法都写成花`,subline:`AI 是你的小本子，把灵感、心情、手账、日常写成可分享的作品。`,icon:xe,primary:`#e879a0`,secondary:`#f9a8d4`,accent:`#6b2d5c`,bg:`#fff3f4`,text:`#4a2542`,muted:`rgba(74,37,66,.68)`,panel:`rgba(255,255,255,.68)`,border:`rgba(232,121,160,.34)`,scene:`floral`,composition:`floral`,features:[`灵感手账`,`日常写作`,`图文生成`],metrics:[{value:`No.01`,label:`灵感号`},{value:`4`,label:`练习`},{value:`花`,label:`输出`}],chips:[`omni-flash`,`Suno 音乐生成 4.5`,`Gemini 3.5 flash`,`grok-4.3`,`VIDU-音乐MV`,`VIDU-解说漫`]},{id:9,name:`团队 AI 工作台`,label:`Team Workspace`,headline:`为团队设计的 AI 工作台`,subline:`一个账号、一处账单、一站集成，把团队需要的 AI 模型像积木一样拼起来。`,icon:C,primary:`#ec7abf`,secondary:`#7c8cff`,accent:`#3b82f6`,bg:`#f3f6ff`,text:`#141936`,muted:`rgba(20,25,54,.68)`,panel:`rgba(255,255,255,.76)`,border:`rgba(124,140,255,.26)`,scene:`teamLight`,composition:`team`,features:[`团队协作`,`账单集中`,`工具栈`],metrics:[{value:`12.8K+`,label:`团队`},{value:`99.99%`,label:`在线率`},{value:`500+`,label:`活跃模型`}],chips:[`omni-flash`,`Suno 音乐生成 4.5`,`Gemini 3.5 flash`,`grok-4.3`,`VIDU Image 2`,`DeepSeek`]},{id:10,name:`模型星环宇宙`,label:`Model Galaxy`,headline:`让 AI 为你生成图片`,subline:`聚合 500+ 全球顶尖大模型，智能对话、图像创作、视频生成和 AI 智能体都在同一平台。`,icon:S,primary:`#00d4ff`,secondary:`#00e6c3`,accent:`#7c3aed`,bg:`#02070b`,text:`#f7fbff`,muted:`rgba(247,251,255,.7)`,panel:`rgba(4,18,24,.68)`,border:`rgba(0,212,255,.34)`,scene:`modelOrbit`,composition:`modelRing`,features:[`模型星环`,`图像生成`,`视频创作`],metrics:[{value:`500+`,label:`AI 模型`},{value:`10K+`,label:`创作者`},{value:`∞`,label:`创造力`}],chips:[`deepseek-v4-flash`,`GPT-5.5`,`Gemini 3.5 flash`,`Suno 音乐生成 4.5`,`VIDU Image 2`,`grok-4.3`,`Pix V5.6`,`omni-flash`,`Claude 4.5`,`Kimi K2`,`Qwen3 Max`,`Midjourney`,`Runway Gen-4`,`Stable Diffusion`,`可灵 2.1`,`豆包 Seedream`,`MiniMax`,`Luma Ray`]}],Ie=X[0];function Le(e){return X.find(t=>t.id===e)||Ie}function Re(e){let t=e.composition===`floral`||e.composition===`team`;return{"--tpl-primary":e.primary,"--tpl-secondary":e.secondary,"--tpl-accent":e.accent,"--tpl-bg":e.bg,"--tpl-text":e.text,"--tpl-muted":e.muted,"--tpl-panel":e.panel,"--tpl-border":e.border,background:t?`radial-gradient(circle at 18% 18%, color-mix(in srgb, ${e.primary} 18%, transparent), transparent 34%), radial-gradient(circle at 78% 16%, color-mix(in srgb, ${e.secondary} 16%, transparent), transparent 34%), radial-gradient(circle at 50% 72%, color-mix(in srgb, ${e.secondary} 18%, transparent), transparent 42%), linear-gradient(135deg, ${e.bg} 0%, #fff 56%, color-mix(in srgb, ${e.bg} 86%, #fff) 100%)`:`radial-gradient(circle at 18% 20%, color-mix(in srgb, ${e.primary} 32%, transparent), transparent 34%), radial-gradient(circle at 82% 18%, color-mix(in srgb, ${e.secondary} 28%, transparent), transparent 36%), radial-gradient(circle at 62% 84%, color-mix(in srgb, ${e.accent} 24%, transparent), transparent 40%), linear-gradient(135deg, ${e.bg} 0%, #05060b 48%, color-mix(in srgb, ${e.bg} 70%, #000) 100%)`}}function ze({scene:e}){let t=Array.from({length:20},(e,t)=>t);return(0,I.jsxs)(`div`,{className:`welcome-scene welcome-scene-${e}`,"aria-hidden":`true`,children:[(0,I.jsx)(`div`,{className:`welcome-grid`}),(0,I.jsx)(`div`,{className:`welcome-orbit welcome-orbit-a`}),(0,I.jsx)(`div`,{className:`welcome-orbit welcome-orbit-b`}),(0,I.jsx)(`div`,{className:`welcome-glow welcome-glow-a`}),(0,I.jsx)(`div`,{className:`welcome-glow welcome-glow-b`}),t.map(e=>(0,I.jsx)(`span`,{className:`welcome-star`,style:{left:`${e*37%100}%`,top:`${e*53%100}%`,animationDelay:`${e%8*-.45}s`}},e)),(0,I.jsx)(`div`,{className:`welcome-scanlines`}),(0,I.jsx)(`div`,{className:`welcome-noise`}),(e===`racing`||e===`solar`)&&(0,I.jsx)(`div`,{className:`welcome-tape`,children:`AI MODEL HUB · SMART LOGIN · CREATIVE WORKSPACE ·`}),e===`solar`&&(0,I.jsx)(`div`,{className:`welcome-sun`})]})}function Be({template:e}){let t=e.icon;return(0,I.jsxs)(`div`,{className:`welcome-visual-wrap`,children:[(0,I.jsx)(`div`,{className:`welcome-halo`}),(0,I.jsxs)(`div`,{className:`welcome-console`,children:[(0,I.jsxs)(`div`,{className:`welcome-console-top`,children:[(0,I.jsxs)(`div`,{className:`welcome-window-dots`,children:[(0,I.jsx)(`span`,{}),(0,I.jsx)(`span`,{}),(0,I.jsx)(`span`,{})]}),(0,I.jsx)(`div`,{className:`welcome-console-title`,children:e.label})]}),(0,I.jsxs)(`div`,{className:`welcome-core`,children:[(0,I.jsx)(`div`,{className:`welcome-core-ring welcome-core-ring-a`}),(0,I.jsx)(`div`,{className:`welcome-core-ring welcome-core-ring-b`}),(0,I.jsx)(`div`,{className:`welcome-cube`,children:(0,I.jsx)(`img`,{src:q,alt:``})}),(0,I.jsx)(`div`,{className:`welcome-core-icon`,children:(0,I.jsx)(t,{size:22})})]}),(0,I.jsx)(`div`,{className:`welcome-flow`,children:e.features.map((e,t)=>(0,I.jsxs)(`div`,{className:`welcome-flow-row`,children:[(0,I.jsx)(`span`,{className:`welcome-flow-dot`}),(0,I.jsx)(`span`,{children:e}),(0,I.jsx)(`span`,{className:`welcome-flow-bar`,style:{width:`${68-t*12}%`}})]},e))}),(0,I.jsx)(`div`,{className:`welcome-model-grid`,children:e.chips.map((e,t)=>(0,I.jsx)(`span`,{className:`welcome-model-chip`,style:{animationDelay:`${t*-.4}s`},children:e},e))})]}),(0,I.jsxs)(`div`,{className:`welcome-float-card welcome-float-left`,children:[(0,I.jsx)(t,{size:18}),(0,I.jsx)(`span`,{children:e.metrics[0].value}),(0,I.jsx)(`small`,{children:e.metrics[0].label})]}),(0,I.jsxs)(`div`,{className:`welcome-float-card welcome-float-right`,children:[(0,I.jsx)(h,{size:18}),(0,I.jsx)(`span`,{children:e.metrics[1].value}),(0,I.jsx)(`small`,{children:e.metrics[1].label})]})]})}function Z({onPrimaryAction:e,label:t=`登录 / 注册`}){return(0,I.jsxs)(`button`,{type:`button`,"data-testid":`welcome-primary-action`,onClick:e,className:`welcome-primary-btn inline-flex h-13 items-center justify-center gap-2 rounded-xl px-7 text-sm font-black text-white transition hover:translate-y-[-1px] focus:outline-none focus:ring-2 focus:ring-white/60`,children:[(0,I.jsx)(`span`,{className:`relative z-10`,children:t}),(0,I.jsx)(_e,{className:`relative z-10`,size:17})]})}var Q=[{pattern:/deepseek/i,icon:le,color:`#4d6bff`,title:`DeepSeek`},{pattern:/gpt|openai/i,icon:t,color:`#f8fafc`,title:`OpenAI`},{pattern:/gemini/i,icon:de,color:`#8ab4f8`,title:`Gemini`},{pattern:/suno/i,icon:re,color:`#ff7a18`,title:`Suno`},{pattern:/vidu/i,icon:se,color:`#f8fafc`,title:`Vidu`},{pattern:/grok/i,icon:ne,color:`#f8fafc`,title:`Grok`},{pattern:/pix/i,icon:D,color:`#8b5cf6`,title:`PixVerse`},{pattern:/claude/i,icon:oe,color:`#d97757`,title:`Claude`},{pattern:/kimi/i,icon:ye,color:`#38bdf8`,title:`Kimi`},{pattern:/qwen/i,icon:ue,color:`#0ea5e9`,title:`Qwen`},{pattern:/midjourney/i,icon:y,color:`#f8fafc`,title:`Midjourney`},{pattern:/runway/i,icon:n,color:`#f8fafc`,title:`Runway`},{pattern:/stable|diffusion/i,icon:_,color:`#8b5cf6`,title:`Stability AI`},{pattern:/可灵|kling/i,icon:k,color:`#5eead4`,title:`Kling`},{pattern:/豆包|doubao/i,icon:ee,color:`#fb7185`,title:`Doubao`},{pattern:/minimax/i,icon:p,color:`#22c55e`,title:`MiniMax`},{pattern:/luma/i,icon:o,color:`#f8fafc`,title:`Luma`}];function $(e){return Q.find(t=>t.pattern.test(e))||{pattern:/./,icon:S,color:`#00d4ff`,title:`AI Model`}}function Ve({modelName:e}){let t=$(e),n=t.icon;return(0,I.jsx)(`span`,{className:`special-model-logo`,style:{"--model-color":t.color},title:t.title,children:(0,I.jsx)(n,{"aria-hidden":`true`,size:34,style:{color:t.color}})})}function He(e,t){let n=360*e/t-90;return{"--orbit-angle":`${n}deg`,"--orbit-counter-angle":`${-n}deg`}}function Ue({template:e,onPrimaryAction:t}){let n=(0,F.useRef)(null);return(0,F.useEffect)(()=>{let e=n.current;if(!e)return;let r=e=>{let n=e.target;n instanceof Element&&n.closest(`.special-orbit-node`)&&t()};return e.addEventListener(`click`,r),()=>{e.removeEventListener(`click`,r)}},[t]),(0,I.jsxs)(`div`,{ref:n,className:`special-model-orbit`,"aria-label":`可点击模型入口`,children:[(0,I.jsx)(`span`,{className:`special-orbit-rotor`,"aria-hidden":`true`}),e.chips.map((n,r)=>(0,I.jsx)(`button`,{type:`button`,className:`special-orbit-node`,style:He(r,e.chips.length),onClick:t,"aria-label":`使用 ${n}，打开登录或注册`,children:(0,I.jsxs)(`span`,{className:`special-orbit-node-inner`,children:[(0,I.jsx)(Ve,{modelName:n}),(0,I.jsx)(`small`,{children:n})]})},n))]})}function We({template:e,onPrimaryAction:t}){let n=e.icon;return e.composition===`gallery`?(0,I.jsxs)(`section`,{className:`special-gallery`,children:[(0,I.jsxs)(`div`,{className:`special-gallery-copy`,children:[(0,I.jsx)(`div`,{className:`special-kicker`,children:`Galleria · Anno 2026`}),(0,I.jsx)(`h1`,{children:e.headline}),(0,I.jsx)(`p`,{children:e.subline}),(0,I.jsxs)(`div`,{className:`special-actions`,children:[(0,I.jsx)(Z,{onPrimaryAction:t,label:`进入画廊`}),(0,I.jsx)(`button`,{type:`button`,className:`special-link-btn`,onClick:t,children:`收藏典藏`})]}),(0,I.jsx)(`div`,{className:`special-gallery-metrics`,children:e.metrics.map(e=>(0,I.jsxs)(`span`,{children:[(0,I.jsx)(`strong`,{children:e.value}),(0,I.jsx)(`small`,{children:e.label})]},e.label))})]}),(0,I.jsx)(`div`,{className:`special-frame-wall`,"aria-hidden":`true`,children:e.chips.map((e,t)=>(0,I.jsxs)(`div`,{className:`special-art-frame special-frame-${t+1}`,children:[(0,I.jsx)(`div`,{className:`special-art-card`,children:t%3==1?(0,I.jsx)(`span`,{className:`special-suno`,children:`Suno`}):(0,I.jsx)(h,{size:70})}),(0,I.jsx)(`span`,{children:e})]},e))})]}):e.composition===`floral`?(0,I.jsxs)(`section`,{className:`special-floral`,children:[(0,I.jsx)(`div`,{className:`special-flower special-flower-a`,children:`✽`}),(0,I.jsx)(`div`,{className:`special-flower special-flower-b`,children:`✿`}),(0,I.jsx)(`div`,{className:`special-flower special-flower-c`,children:`✾`}),(0,I.jsx)(`div`,{className:`special-stamp`,children:`No. 01 · 灵感号`}),(0,I.jsx)(`h1`,{children:e.headline}),(0,I.jsx)(`div`,{className:`special-divider`,children:`✽`}),(0,I.jsx)(`p`,{children:e.subline}),(0,I.jsxs)(`div`,{className:`special-actions`,children:[(0,I.jsx)(Z,{onPrimaryAction:t,label:`翻开新一页`}),(0,I.jsx)(`button`,{type:`button`,className:`special-link-btn`,onClick:t,children:`合作邀约`})]}),(0,I.jsx)(`blockquote`,{children:`灵感就像花瓣，留住它的方式是写下来。`}),(0,I.jsx)(`div`,{className:`special-sticker-row`,children:e.chips.map(e=>(0,I.jsx)(`span`,{children:e},e))})]}):e.composition===`team`?(0,I.jsxs)(`section`,{className:`special-team`,children:[(0,I.jsxs)(`div`,{className:`special-team-copy`,children:[(0,I.jsx)(`div`,{className:`special-live-pill`,children:`v3.0 · LIVE`}),(0,I.jsx)(`h1`,{children:e.headline}),(0,I.jsx)(`p`,{children:e.subline}),(0,I.jsxs)(`div`,{className:`special-actions`,children:[(0,I.jsx)(Z,{onPrimaryAction:t,label:`立即开始`}),(0,I.jsx)(`button`,{type:`button`,className:`special-doc-btn`,onClick:t,children:`查看文档`})]}),(0,I.jsx)(`div`,{className:`special-team-metrics`,children:e.metrics.map(e=>(0,I.jsxs)(`span`,{children:[(0,I.jsx)(`strong`,{children:e.value}),(0,I.jsx)(`small`,{children:e.label})]},e.label))})]}),(0,I.jsxs)(`div`,{className:`special-team-stack`,children:[(0,I.jsxs)(`div`,{className:`special-window-card`,children:[(0,I.jsxs)(`div`,{className:`welcome-window-dots`,children:[(0,I.jsx)(`span`,{}),(0,I.jsx)(`span`,{}),(0,I.jsx)(`span`,{})]}),(0,I.jsx)(`strong`,{children:`workspace.app`}),(0,I.jsx)(`i`,{}),(0,I.jsx)(`i`,{}),(0,I.jsx)(`i`,{})]}),(0,I.jsxs)(`div`,{className:`special-tool-card`,children:[(0,I.jsx)(`strong`,{children:`你的工具栈`}),(0,I.jsx)(`div`,{children:e.chips.slice(0,6).map(e=>(0,I.jsxs)(`span`,{children:[(0,I.jsx)(n,{size:24}),e]},e))})]}),(0,I.jsxs)(`div`,{className:`special-mini-card`,children:[(0,I.jsx)(h,{size:16}),(0,I.jsx)(`span`,{children:`500+`}),(0,I.jsx)(`small`,{children:`活跃模型`})]})]})]}):e.composition===`modelRing`?(0,I.jsxs)(`section`,{className:`special-model-ring`,children:[(0,I.jsx)(Ue,{template:e,onPrimaryAction:t}),(0,I.jsxs)(`div`,{className:`special-ring-copy`,children:[(0,I.jsx)(`div`,{className:`special-live-pill`,children:`新一代 AI 平台`}),(0,I.jsx)(`h1`,{children:e.headline}),(0,I.jsx)(`p`,{children:e.subline}),(0,I.jsxs)(`div`,{className:`special-actions`,children:[(0,I.jsx)(Z,{onPrimaryAction:t,label:`开始使用`}),(0,I.jsx)(`button`,{type:`button`,className:`special-doc-btn dark`,onClick:t,children:`商务合作`})]}),(0,I.jsx)(`div`,{className:`special-team-metrics`,children:e.metrics.map(e=>(0,I.jsxs)(`span`,{children:[(0,I.jsx)(`strong`,{children:e.value}),(0,I.jsx)(`small`,{children:e.label})]},e.label))})]})]}):(0,I.jsxs)(`section`,{className:`special-dream`,children:[(0,I.jsxs)(`div`,{className:`special-kicker`,children:[(0,I.jsx)(n,{size:14}),` AI 创作新维度`]}),(0,I.jsx)(`h1`,{children:e.headline}),(0,I.jsx)(`p`,{children:e.subline}),(0,I.jsxs)(`div`,{className:`special-actions`,children:[(0,I.jsx)(Z,{onPrimaryAction:t,label:`开启魔法`}),(0,I.jsx)(`button`,{type:`button`,className:`special-doc-btn dark`,onClick:t,children:`商务合作`})]}),(0,I.jsx)(`div`,{className:`special-pill-cloud`,children:e.chips.map(e=>(0,I.jsx)(`span`,{children:e},e))})]})}function Ge(){return(0,I.jsx)(`style`,{children:`
      .welcome-root {
        color: var(--tpl-text);
      }
      .welcome-scene {
        position: fixed;
        inset: 0;
        z-index: 0;
        overflow: hidden;
        pointer-events: none;
      }
      .welcome-grid {
        position: absolute;
        inset: -2px;
        background-image:
          linear-gradient(rgba(255,255,255,.055) 1px, transparent 1px),
          linear-gradient(90deg, rgba(255,255,255,.055) 1px, transparent 1px);
        background-size: 56px 56px;
        mask-image: radial-gradient(ellipse at 50% 42%, black 0%, transparent 76%);
        -webkit-mask-image: radial-gradient(ellipse at 50% 42%, black 0%, transparent 76%);
        animation: welcome-grid-drift 16s linear infinite;
      }
      .welcome-glow {
        position: absolute;
        border-radius: 999px;
        filter: blur(96px);
        opacity: .48;
        mix-blend-mode: screen;
        animation: welcome-blob 16s ease-in-out infinite;
      }
      .welcome-glow-a {
        width: 48rem;
        height: 48rem;
        left: -16rem;
        top: -14rem;
        background: var(--tpl-primary);
      }
      .welcome-glow-b {
        width: 42rem;
        height: 42rem;
        right: -14rem;
        bottom: -12rem;
        background: var(--tpl-secondary);
        animation-delay: -7s;
      }
      .welcome-orbit {
        position: absolute;
        border: 1px solid color-mix(in srgb, var(--tpl-primary) 42%, transparent);
        border-radius: 999px;
        box-shadow: inset 0 0 32px color-mix(in srgb, var(--tpl-primary) 16%, transparent);
        opacity: .42;
        animation: welcome-spin 18s linear infinite;
      }
      .welcome-orbit-a {
        width: 42rem;
        height: 42rem;
        right: 10%;
        top: 14%;
      }
      .welcome-orbit-b {
        width: 24rem;
        height: 24rem;
        left: 4%;
        bottom: 8%;
        animation-duration: 24s;
        animation-direction: reverse;
      }
      .welcome-star {
        position: absolute;
        width: 2px;
        height: 2px;
        border-radius: 50%;
        background: var(--tpl-text);
        opacity: .52;
        box-shadow: 0 0 12px var(--tpl-primary);
        animation: welcome-twinkle 3.2s ease-in-out infinite;
      }
      .welcome-scanlines {
        position: absolute;
        inset: 0;
        background: repeating-linear-gradient(180deg, transparent 0, transparent 2px, rgba(255,255,255,.026) 2px, rgba(255,255,255,.026) 4px);
        opacity: .42;
      }
      .welcome-noise {
        position: absolute;
        inset: 0;
        opacity: .11;
        mix-blend-mode: overlay;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.6'/%3E%3C/svg%3E");
      }
      .welcome-tape {
        position: absolute;
        left: -10%;
        right: -10%;
        top: 12%;
        transform: rotate(-2deg);
        padding: .5rem 0;
        background: linear-gradient(90deg, var(--tpl-primary), var(--tpl-secondary), var(--tpl-accent));
        color: #fff;
        font-size: .75rem;
        font-weight: 900;
        letter-spacing: .22em;
        text-align: center;
        opacity: .66;
        box-shadow: 0 0 32px color-mix(in srgb, var(--tpl-primary) 45%, transparent);
      }
      .welcome-sun {
        position: absolute;
        width: 22rem;
        height: 22rem;
        right: 12%;
        top: 18%;
        border-radius: 50%;
        background: radial-gradient(circle at 50% 30%, var(--tpl-accent), var(--tpl-primary) 42%, transparent 72%);
        box-shadow: 0 0 80px color-mix(in srgb, var(--tpl-primary) 50%, transparent);
        opacity: .68;
      }
      .welcome-scene-glass .welcome-grid {
        background-size: 80px 80px;
        opacity: .5;
      }
      .welcome-scene-terminal .welcome-grid,
      .welcome-scene-cyber .welcome-grid {
        background-size: 46px 46px;
      }
      .welcome-scene-luxury .welcome-grid {
        opacity: .22;
      }
      .welcome-scene-floral .welcome-grid,
      .welcome-scene-teamLight .welcome-grid {
        background-image:
          linear-gradient(rgba(124,140,255,.08) 1px, transparent 1px),
          linear-gradient(90deg, rgba(124,140,255,.08) 1px, transparent 1px);
        opacity: .24;
      }
      .welcome-scene-floral .welcome-scanlines,
      .welcome-scene-teamLight .welcome-scanlines {
        display: none;
      }
      .welcome-scene-modelOrbit .welcome-grid {
        background-size: 64px 64px;
        opacity: .72;
      }
      .welcome-scene-dream .welcome-grid {
        opacity: .28;
      }
      .welcome-shell {
        position: relative;
        z-index: 1;
      }
      .welcome-brand-mark {
        box-shadow: 0 0 28px color-mix(in srgb, var(--tpl-primary) 38%, transparent);
      }
      .welcome-badge,
      .welcome-chip,
      .welcome-metric,
      .welcome-console,
      .welcome-float-card {
        border: 1px solid var(--tpl-border);
        background: linear-gradient(145deg, color-mix(in srgb, var(--tpl-panel) 92%, transparent), rgba(255,255,255,.045));
        box-shadow: 0 24px 80px rgba(0,0,0,.32), inset 0 1px 0 rgba(255,255,255,.08);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
      }
      .welcome-title-gradient {
        background: linear-gradient(100deg, var(--tpl-text) 0%, color-mix(in srgb, var(--tpl-primary) 72%, #fff) 42%, color-mix(in srgb, var(--tpl-secondary) 72%, #fff) 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        text-shadow: 0 0 34px color-mix(in srgb, var(--tpl-primary) 22%, transparent);
      }
      .welcome-primary-btn {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, var(--tpl-primary), var(--tpl-secondary));
        box-shadow: 0 18px 44px color-mix(in srgb, var(--tpl-primary) 32%, transparent), 0 0 0 1px rgba(255,255,255,.16) inset;
      }
      .welcome-primary-btn:before {
        content: "";
        position: absolute;
        inset: 0;
        transform: translateX(-120%);
        background: linear-gradient(90deg, transparent, rgba(255,255,255,.36), transparent);
        animation: welcome-sweep 2.8s ease-in-out infinite;
      }
      .welcome-visual-wrap {
        position: relative;
        min-height: 31rem;
      }
      .welcome-halo {
        position: absolute;
        inset: 7% 8%;
        border-radius: 999px;
        background: conic-gradient(from 0deg, var(--tpl-primary), var(--tpl-secondary), var(--tpl-accent), var(--tpl-primary));
        filter: blur(34px);
        opacity: .34;
        animation: welcome-spin 12s linear infinite;
      }
      .welcome-console {
        position: relative;
        min-height: 29rem;
        border-radius: 2rem;
        padding: 1.1rem;
        overflow: hidden;
      }
      .welcome-console:before {
        content: "";
        position: absolute;
        inset: 0;
        background:
          linear-gradient(115deg, transparent 0%, rgba(255,255,255,.12) 38%, transparent 54%),
          radial-gradient(circle at 50% 10%, color-mix(in srgb, var(--tpl-primary) 22%, transparent), transparent 48%);
        opacity: .75;
        pointer-events: none;
      }
      .welcome-console-top,
      .welcome-core,
      .welcome-flow,
      .welcome-model-grid {
        position: relative;
        z-index: 1;
      }
      .welcome-console-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid var(--tpl-border);
        padding-bottom: .9rem;
      }
      .welcome-window-dots {
        display: flex;
        gap: .45rem;
      }
      .welcome-window-dots span {
        width: .72rem;
        height: .72rem;
        border-radius: 50%;
        background: var(--tpl-primary);
        box-shadow: 0 0 16px var(--tpl-primary);
      }
      .welcome-window-dots span:nth-child(2) {
        background: var(--tpl-secondary);
        box-shadow: 0 0 16px var(--tpl-secondary);
      }
      .welcome-window-dots span:nth-child(3) {
        background: rgba(255,255,255,.32);
        box-shadow: none;
      }
      .welcome-console-title {
        color: var(--tpl-muted);
        font-size: .78rem;
        font-weight: 700;
        letter-spacing: .08em;
        text-transform: uppercase;
      }
      .welcome-core {
        display: grid;
        place-items: center;
        height: 14rem;
        margin: 1.2rem 0;
      }
      .welcome-core-ring {
        position: absolute;
        border: 1px solid color-mix(in srgb, var(--tpl-primary) 45%, transparent);
        border-radius: 999px;
        box-shadow: 0 0 30px color-mix(in srgb, var(--tpl-primary) 18%, transparent);
      }
      .welcome-core-ring-a {
        width: 13rem;
        height: 13rem;
        animation: welcome-spin 13s linear infinite;
      }
      .welcome-core-ring-b {
        width: 9rem;
        height: 9rem;
        border-color: color-mix(in srgb, var(--tpl-secondary) 46%, transparent);
        animation: welcome-spin 10s linear infinite reverse;
      }
      .welcome-cube {
        position: relative;
        display: grid;
        place-items: center;
        width: 8.8rem;
        height: 8.8rem;
        border-radius: 2rem;
        background: linear-gradient(145deg, rgba(255,255,255,.18), rgba(255,255,255,.04));
        border: 1px solid var(--tpl-border);
        box-shadow: 0 0 55px color-mix(in srgb, var(--tpl-primary) 32%, transparent);
        animation: welcome-float 5s ease-in-out infinite;
      }
      .welcome-cube img {
        width: 84%;
        height: 84%;
        object-fit: contain;
        filter: drop-shadow(0 18px 26px rgba(0,0,0,.44));
      }
      .welcome-core-icon {
        position: absolute;
        right: 21%;
        top: 21%;
        display: grid;
        place-items: center;
        width: 3rem;
        height: 3rem;
        border-radius: 1rem;
        color: #fff;
        background: linear-gradient(135deg, var(--tpl-primary), var(--tpl-secondary));
        box-shadow: 0 0 28px color-mix(in srgb, var(--tpl-primary) 52%, transparent);
      }
      .welcome-flow {
        display: grid;
        gap: .65rem;
      }
      .welcome-flow-row {
        display: grid;
        grid-template-columns: auto minmax(4rem, 1fr) 32%;
        align-items: center;
        gap: .65rem;
        min-height: 2.65rem;
        border: 1px solid var(--tpl-border);
        border-radius: .95rem;
        padding: .55rem .75rem;
        color: var(--tpl-text);
        background: rgba(255,255,255,.055);
      }
      .welcome-flow-dot {
        width: .52rem;
        height: .52rem;
        border-radius: 50%;
        background: var(--tpl-primary);
        box-shadow: 0 0 14px var(--tpl-primary);
      }
      .welcome-flow-bar {
        justify-self: end;
        height: .36rem;
        border-radius: 99px;
        background: linear-gradient(90deg, var(--tpl-primary), var(--tpl-secondary));
        animation: welcome-pulse 2.4s ease-in-out infinite;
      }
      .welcome-model-grid {
        display: flex;
        flex-wrap: wrap;
        gap: .55rem;
        margin-top: 1rem;
      }
      .welcome-model-chip {
        border: 1px solid var(--tpl-border);
        border-radius: 999px;
        padding: .5rem .72rem;
        color: var(--tpl-muted);
        background: rgba(255,255,255,.06);
        font-size: .72rem;
        font-weight: 700;
        animation: welcome-chip-glow 3s ease-in-out infinite;
      }
      .welcome-float-card {
        position: absolute;
        z-index: 3;
        display: grid;
        gap: .1rem;
        min-width: 8.5rem;
        border-radius: 1.25rem;
        padding: .9rem 1rem;
        color: var(--tpl-text);
        animation: welcome-float 5.4s ease-in-out infinite;
      }
      .welcome-float-card svg {
        color: var(--tpl-primary);
      }
      .welcome-float-card span {
        font-size: 1.15rem;
        font-weight: 900;
      }
      .welcome-float-card small {
        color: var(--tpl-muted);
        font-size: .72rem;
      }
      .welcome-float-left {
        left: -1rem;
        top: 5.5rem;
      }
      .welcome-float-right {
        right: -1rem;
        bottom: 5.5rem;
        animation-delay: -2s;
      }
      .special-dream,
      .special-floral,
      .special-model-ring {
        position: relative;
        z-index: 1;
        display: flex;
        min-height: calc(100vh - 8rem);
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 3rem 0 5rem;
      }
      .special-dream h1,
      .special-model-ring h1 {
        max-width: 52rem;
        margin: 1.2rem 0 0;
        color: var(--tpl-text);
        font-size: clamp(4rem, 9vw, 8.4rem);
        font-weight: 950;
        line-height: .9;
        letter-spacing: 0;
        background: linear-gradient(120deg, #fff 0%, var(--tpl-primary) 46%, var(--tpl-accent) 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        text-shadow: 0 0 60px color-mix(in srgb, var(--tpl-primary) 24%, transparent);
      }
      .special-dream p,
      .special-model-ring p,
      .special-floral p,
      .special-gallery p,
      .special-team p {
        max-width: 48rem;
        margin: 1.5rem auto 0;
        color: var(--tpl-muted);
        font-size: 1.05rem;
        line-height: 1.9;
      }
      .special-kicker,
      .special-live-pill,
      .special-stamp {
        display: inline-flex;
        align-items: center;
        gap: .45rem;
        border: 1px solid var(--tpl-border);
        border-radius: 999px;
        padding: .45rem .9rem;
        color: var(--tpl-muted);
        background: color-mix(in srgb, var(--tpl-panel) 74%, transparent);
        box-shadow: inset 0 1px 0 rgba(255,255,255,.08);
        font-size: .76rem;
        font-weight: 800;
        letter-spacing: .04em;
      }
      .special-actions {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin-top: 2rem;
        flex-wrap: wrap;
      }
      .special-link-btn,
      .special-doc-btn {
        min-height: 3.25rem;
        border-radius: 999px;
        border: 1px solid var(--tpl-border);
        padding: 0 1.5rem;
        color: var(--tpl-muted);
        background: color-mix(in srgb, var(--tpl-panel) 74%, transparent);
        font-weight: 800;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
      }
      .special-doc-btn {
        color: var(--tpl-text);
        background: rgba(255,255,255,.76);
      }
      .special-doc-btn.dark {
        color: var(--tpl-muted);
        background: rgba(255,255,255,.075);
      }
      .special-pill-cloud {
        display: flex;
        max-width: 48rem;
        flex-wrap: wrap;
        justify-content: center;
        gap: .65rem;
        margin-top: 2.8rem;
      }
      .special-pill-cloud span,
      .special-sticker-row span {
        border: 1px solid var(--tpl-border);
        border-radius: 999px;
        padding: .55rem .85rem;
        color: var(--tpl-muted);
        background: color-mix(in srgb, var(--tpl-panel) 78%, transparent);
        box-shadow: 0 14px 34px rgba(0,0,0,.18);
        font-size: .78rem;
        font-weight: 800;
      }
      .special-gallery {
        display: grid;
        min-height: calc(100vh - 7rem);
        grid-template-columns: minmax(0, .85fr) minmax(32rem, 1fr);
        align-items: center;
        gap: 4rem;
        padding: 4rem 0 7rem;
      }
      .special-gallery-copy {
        max-width: 38rem;
      }
      .special-gallery h1 {
        margin: 1.1rem 0 0;
        color: var(--tpl-text);
        font-family: Georgia, "Times New Roman", serif;
        font-size: clamp(4rem, 7vw, 7rem);
        font-weight: 500;
        line-height: 1.02;
        letter-spacing: 0;
      }
      .special-gallery-metrics {
        display: flex;
        gap: 1.6rem;
        margin-top: 2.4rem;
        border-top: 1px solid var(--tpl-border);
        border-bottom: 1px solid var(--tpl-border);
        padding: 1.2rem 0;
      }
      .special-gallery-metrics span,
      .special-team-metrics span {
        display: grid;
        gap: .18rem;
      }
      .special-gallery-metrics strong,
      .special-team-metrics strong {
        color: var(--tpl-text);
        font-size: 1.8rem;
        line-height: 1;
      }
      .special-gallery-metrics small,
      .special-team-metrics small {
        color: var(--tpl-muted);
        font-size: .78rem;
      }
      .special-frame-wall {
        position: relative;
        min-height: 34rem;
      }
      .special-art-frame {
        position: absolute;
        display: grid;
        gap: .6rem;
        place-items: center;
        color: var(--tpl-primary);
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        font-weight: 800;
      }
      .special-art-card {
        display: grid;
        place-items: center;
        width: 11.5rem;
        height: 15rem;
        border: .55rem solid var(--tpl-primary);
        outline: 2px solid color-mix(in srgb, var(--tpl-primary) 54%, transparent);
        outline-offset: -.9rem;
        background: #12131a;
        color: var(--tpl-accent);
        box-shadow: 0 24px 54px rgba(0,0,0,.38);
      }
      .special-frame-1 { left: 18%; top: 0; transform: rotate(-3deg); }
      .special-frame-2 { right: 10%; top: 2rem; transform: rotate(3deg); }
      .special-frame-3 { left: 26%; bottom: 0; transform: rotate(-1deg); }
      .special-frame-4 { right: 5%; bottom: 2rem; transform: rotate(4deg); }
      .special-frame-wall .special-art-frame:nth-child(n+5) { display: none; }
      .special-suno {
        color: #fff;
        background: radial-gradient(circle, #facc15, #ef4444 60%, #ec4899);
        display: grid;
        place-items: center;
        width: 7rem;
        height: 7rem;
        border-radius: 50%;
        font-size: 1.6rem;
        text-transform: uppercase;
      }
      .special-floral {
        color: var(--tpl-text);
        overflow: hidden;
      }
      .special-floral h1 {
        max-width: 54rem;
        margin: 1.2rem 0 0;
        color: var(--tpl-text);
        font-family: Georgia, "Times New Roman", serif;
        font-size: clamp(3.8rem, 7vw, 7rem);
        font-weight: 700;
        line-height: 1.06;
      }
      .special-divider {
        margin-top: 1rem;
        color: var(--tpl-primary);
        font-size: 1.6rem;
      }
      .special-floral blockquote {
        margin: 2.4rem 0 0;
        color: color-mix(in srgb, var(--tpl-primary) 86%, #fff);
        font-size: 1.15rem;
        font-style: italic;
      }
      .special-sticker-row {
        display: flex;
        max-width: 44rem;
        flex-wrap: wrap;
        justify-content: center;
        gap: .7rem;
        margin-top: 2.8rem;
      }
      .special-sticker-row span {
        border-style: dashed;
        border-radius: .35rem;
        color: var(--tpl-muted);
        background: rgba(255,255,255,.52);
        transform: rotate(var(--sticker-rotate, -2deg));
      }
      .special-sticker-row span:nth-child(2n) {
        --sticker-rotate: 2deg;
      }
      .special-flower {
        position: absolute;
        color: color-mix(in srgb, var(--tpl-primary) 45%, transparent);
        font-size: 2rem;
        animation: welcome-float 6s ease-in-out infinite;
      }
      .special-flower-a { left: 10%; top: 24%; }
      .special-flower-b { right: 12%; top: 32%; animation-delay: -2s; }
      .special-flower-c { left: 18%; bottom: 16%; animation-delay: -4s; }
      .special-team {
        display: grid;
        min-height: calc(100vh - 7rem);
        grid-template-columns: minmax(0, .85fr) minmax(30rem, 1fr);
        align-items: center;
        gap: 4rem;
        padding: 4rem 0 8rem;
        color: var(--tpl-text);
      }
      .special-team h1 {
        max-width: 42rem;
        margin: 1.6rem 0 0;
        color: var(--tpl-text);
        font-size: clamp(3.8rem, 6.4vw, 7rem);
        font-weight: 950;
        line-height: .98;
      }
      .special-team h1::first-line {
        color: var(--tpl-text);
      }
      .special-team h1 {
        background: linear-gradient(120deg, var(--tpl-text) 0%, var(--tpl-primary) 58%, var(--tpl-secondary) 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
      }
      .special-team-metrics {
        display: flex;
        gap: 2rem;
        margin-top: 2.2rem;
      }
      .special-team-stack {
        position: relative;
        min-height: 34rem;
      }
      .special-window-card,
      .special-tool-card,
      .special-mini-card {
        position: absolute;
        border: 1px solid var(--tpl-border);
        border-radius: 1.6rem;
        background: rgba(255,255,255,.82);
        box-shadow: 0 32px 80px rgba(99,102,241,.16);
        color: var(--tpl-text);
      }
      .special-window-card {
        right: 2rem;
        top: 1rem;
        width: 24rem;
        padding: 1.7rem;
      }
      .special-window-card strong {
        float: right;
        color: var(--tpl-muted);
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      }
      .special-window-card i {
        display: block;
        height: .8rem;
        margin-top: .8rem;
        border-radius: 999px;
        background: linear-gradient(90deg, var(--tpl-primary), var(--tpl-secondary), var(--tpl-accent));
      }
      .special-window-card i:nth-of-type(2) { width: 72%; }
      .special-window-card i:nth-of-type(3) { width: 88%; }
      .special-tool-card {
        right: 5rem;
        bottom: 0;
        width: 24rem;
        padding: 1.5rem;
      }
      .special-tool-card > strong {
        display: block;
        text-align: right;
        margin-bottom: 1rem;
      }
      .special-tool-card div {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: .7rem;
      }
      .special-tool-card span {
        display: grid;
        place-items: center;
        min-height: 5.6rem;
        border-radius: .7rem;
        background: #14151d;
        color: #fff;
        font-size: .65rem;
        text-align: center;
        gap: .3rem;
      }
      .special-mini-card {
        left: 0;
        top: 48%;
        display: grid;
        gap: .5rem;
        padding: 1.6rem;
        min-width: 13rem;
      }
      .special-mini-card span {
        font-size: 2.4rem;
        font-weight: 950;
        background: linear-gradient(120deg, var(--tpl-primary), var(--tpl-secondary));
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
      }
      .special-model-ring {
        min-height: calc(100vh - 7rem);
        background: rgba(0,0,0,.001);
        overflow: hidden;
      }
      .special-ring-copy {
        position: relative;
        z-index: 2;
        display: flex;
        flex-direction: column;
        align-items: center;
      }
      .special-model-orbit {
        position: absolute;
        inset: 2rem 0 0;
        z-index: 3;
        --orbit-size: min(64rem, 88vw, calc(100vh - 7rem));
        --orbit-radius: calc(var(--orbit-size) / 2 - 4.6rem);
        width: var(--orbit-size);
        height: var(--orbit-size);
        margin: auto;
        overflow: visible;
        border: 1px solid color-mix(in srgb, var(--tpl-primary) 20%, transparent);
        border-radius: 50%;
        background: rgba(0,0,0,.001);
        box-shadow: 0 0 80px color-mix(in srgb, var(--tpl-primary) 14%, transparent);
        pointer-events: none;
      }
      .special-orbit-rotor {
        position: absolute;
        inset: 0;
        border-radius: 50%;
        background:
          conic-gradient(from 0deg, transparent 0deg, color-mix(in srgb, var(--tpl-primary) 46%, transparent) 34deg, transparent 74deg, transparent 180deg, color-mix(in srgb, var(--tpl-secondary) 34%, transparent) 218deg, transparent 268deg),
          radial-gradient(circle, transparent 0 54%, color-mix(in srgb, var(--tpl-primary) 14%, transparent) 55%, transparent 56%);
        animation: welcome-spin 42s linear infinite;
        pointer-events: none;
      }
      .special-model-orbit:hover .special-orbit-rotor {
        animation-play-state: paused;
      }
      .special-model-orbit:has(.special-orbit-node:hover) .special-orbit-rotor,
      .special-model-orbit:has(.special-orbit-node:focus-visible) .special-orbit-rotor {
        animation-play-state: paused;
      }
      .special-model-orbit:hover .special-orbit-node {
        animation-play-state: paused;
      }
      .special-model-orbit:has(.special-orbit-node:hover) .special-orbit-node,
      .special-model-orbit:has(.special-orbit-node:focus-visible) .special-orbit-node {
        animation-play-state: paused;
      }
      .special-model-orbit:before,
      .special-model-orbit:after {
        content: "";
        position: absolute;
        inset: 14%;
        border: 1px solid color-mix(in srgb, var(--tpl-secondary) 18%, transparent);
        border-radius: 50%;
        pointer-events: none;
      }
      .special-model-orbit:after {
        inset: 29%;
      }
      .special-orbit-node {
        position: absolute;
        left: 50%;
        top: 50%;
        display: grid;
        place-items: center;
        gap: .3rem;
        width: 7.2rem;
        height: 5.2rem;
        border: 0;
        padding: 0;
        background: transparent;
        color: var(--tpl-muted);
        cursor: pointer;
        opacity: .72;
        transform-origin: center;
        transform: translate(-50%, -50%) rotate(var(--orbit-angle)) translateX(var(--orbit-radius)) rotate(var(--orbit-counter-angle));
        animation: welcome-orbit-node 44s linear infinite;
        transition: color .22s ease, filter .22s ease, opacity .22s ease;
        pointer-events: auto;
        z-index: 2;
        will-change: transform;
      }
      .special-orbit-node-inner {
        display: grid;
        place-items: center;
        gap: .3rem;
        width: 100%;
        transform-origin: center;
        transition: transform .22s ease;
      }
      .special-orbit-node * {
        pointer-events: none;
      }
      .special-orbit-node:hover,
      .special-orbit-node:focus-visible {
        z-index: 5;
        color: var(--tpl-text);
        opacity: 1;
        filter: drop-shadow(0 0 24px color-mix(in srgb, var(--tpl-primary) 48%, transparent));
      }
      .special-orbit-node:hover .special-orbit-node-inner,
      .special-orbit-node:focus-visible .special-orbit-node-inner {
        transform: scale(1.32);
      }
      .special-orbit-node:focus-visible {
        outline: 2px solid var(--tpl-primary);
        outline-offset: .35rem;
        border-radius: 1rem;
      }
      .special-model-logo {
        display: grid;
        place-items: center;
        width: 3.35rem;
        height: 3.35rem;
        overflow: visible;
        border: 1px solid var(--tpl-border);
        border-radius: 1rem;
        background:
          radial-gradient(circle at 30% 18%, color-mix(in srgb, var(--model-color) 35%, transparent), transparent 44%),
          rgba(3, 7, 18, .72);
        box-shadow: 0 0 22px color-mix(in srgb, var(--model-color) 24%, transparent);
        transition: box-shadow .22s ease, border-color .22s ease;
      }
      .special-model-logo svg {
        display: block;
        width: 2.15rem;
        height: 2.15rem;
        max-width: 2.15rem;
        max-height: 2.15rem;
        overflow: visible;
      }
      .special-orbit-node:hover .special-model-logo,
      .special-orbit-node:focus-visible .special-model-logo {
        border-color: color-mix(in srgb, var(--model-color) 76%, white);
        box-shadow: 0 0 36px color-mix(in srgb, var(--model-color) 46%, transparent), 0 0 0 6px color-mix(in srgb, var(--model-color) 14%, transparent);
      }
      .special-orbit-node small {
        font-size: .65rem;
        max-width: 7.5rem;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      @keyframes welcome-grid-drift {
        from { transform: translate3d(0,0,0); }
        to { transform: translate3d(56px,56px,0); }
      }
      @keyframes welcome-blob {
        0%, 100% { transform: translate3d(0,0,0) scale(1); }
        50% { transform: translate3d(48px,-28px,0) scale(1.08); }
      }
      @keyframes welcome-spin {
        to { transform: rotate(360deg); }
      }
      @keyframes welcome-orbit-node {
        from {
          transform: translate(-50%, -50%) rotate(var(--orbit-angle)) translateX(var(--orbit-radius)) rotate(var(--orbit-counter-angle));
        }
        to {
          transform: translate(-50%, -50%) rotate(calc(var(--orbit-angle) + 360deg)) translateX(var(--orbit-radius)) rotate(calc(var(--orbit-counter-angle) - 360deg));
        }
      }
      @keyframes welcome-twinkle {
        0%, 100% { opacity: .18; transform: scale(.8); }
        50% { opacity: .9; transform: scale(1.35); }
      }
      @keyframes welcome-sweep {
        0% { transform: translateX(-120%); }
        45%, 100% { transform: translateX(120%); }
      }
      @keyframes welcome-float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-12px); }
      }
      @keyframes welcome-pulse {
        0%, 100% { opacity: .55; }
        50% { opacity: 1; }
      }
      @keyframes welcome-chip-glow {
        0%, 100% { box-shadow: 0 0 0 color-mix(in srgb, var(--tpl-primary) 0%, transparent); }
        50% { box-shadow: 0 0 18px color-mix(in srgb, var(--tpl-primary) 28%, transparent); }
      }
      @media (max-width: 1024px) {
        .special-gallery,
        .special-team {
          grid-template-columns: 1fr;
          gap: 2.5rem;
        }
        .special-gallery-copy,
        .special-team-copy {
          max-width: none;
        }
        .special-frame-wall,
        .special-team-stack {
          min-height: 30rem;
        }
        .welcome-visual-wrap {
          min-height: 27rem;
        }
        .welcome-console {
          min-height: 26rem;
        }
        .welcome-float-card {
          display: none;
        }
      }
      @media (max-width: 640px) {
        .special-dream,
        .special-floral,
        .special-model-ring {
          min-height: auto;
          padding: 4rem 0 3rem;
        }
        .special-dream h1,
        .special-model-ring h1,
        .special-floral h1,
        .special-gallery h1,
        .special-team h1 {
          font-size: clamp(3rem, 17vw, 4.7rem);
        }
        .special-gallery,
        .special-team {
          padding: 3rem 0 4rem;
        }
        .special-gallery-metrics,
        .special-team-metrics {
          gap: 1rem;
          flex-wrap: wrap;
        }
        .special-frame-wall {
          min-height: 28rem;
          transform: scale(.82);
          transform-origin: top center;
        }
        .special-window-card,
        .special-tool-card {
          position: relative;
          right: auto;
          bottom: auto;
          top: auto;
          width: 100%;
        }
        .special-team-stack {
          display: grid;
          min-height: auto;
          gap: 1rem;
        }
        .special-mini-card {
          position: relative;
          left: auto;
          top: auto;
        }
        .special-tool-card div {
          grid-template-columns: repeat(2, 1fr);
        }
        .special-model-orbit {
          inset: 5rem 0 auto;
          --orbit-size: min(28rem, 92vw, calc(100vh - 10rem));
          --orbit-radius: calc(var(--orbit-size) / 2 - 4.4rem);
          opacity: .3;
        }
        .special-model-logo {
          width: 2.9rem;
          height: 2.9rem;
        }
        .special-model-logo svg {
          width: 1.9rem;
          height: 1.9rem;
          max-width: 1.9rem;
          max-height: 1.9rem;
        }
        .special-orbit-node small {
          display: none;
        }
        .welcome-root {
          background-attachment: scroll;
        }
        .welcome-grid {
          background-size: 42px 42px;
        }
        .welcome-orbit {
          opacity: .24;
        }
        .welcome-visual-wrap {
          min-height: 25rem;
        }
        .welcome-console {
          min-height: 24rem;
          border-radius: 1.5rem;
          padding: .85rem;
        }
        .welcome-core {
          height: 11.5rem;
        }
        .welcome-core-ring-a {
          width: 10.5rem;
          height: 10.5rem;
        }
        .welcome-core-ring-b {
          width: 7.4rem;
          height: 7.4rem;
        }
        .welcome-cube {
          width: 7rem;
          height: 7rem;
          border-radius: 1.5rem;
        }
        .welcome-core-icon {
          right: 16%;
          top: 18%;
        }
        .welcome-flow-row {
          grid-template-columns: auto 1fr;
        }
        .welcome-flow-bar {
          display: none;
        }
        .welcome-tape {
          top: 9%;
          font-size: .62rem;
        }
      }
    `})}function Ke({templateId:e,siteName:t,siteIcon:n,onPrimaryAction:r}){let i=Le(e),a=i.icon;return(0,I.jsxs)(`main`,{className:`welcome-root fixed inset-0 z-50 min-h-screen overflow-y-auto px-5 py-5 text-left font-sans sm:px-8 lg:px-10`,"data-testid":`welcome-gate`,"data-welcome-template-id":String(i.id),"data-welcome-template-name":i.name,"data-welcome-template-scene":i.scene,"data-welcome-template-composition":i.composition||`split`,style:Re(i),children:[(0,I.jsx)(Ge,{}),(0,I.jsx)(ze,{scene:i.scene}),(0,I.jsxs)(`div`,{className:`welcome-shell mx-auto flex min-h-[calc(100vh-40px)] w-full max-w-7xl flex-col`,children:[(0,I.jsx)(`header`,{className:`flex items-center justify-between gap-4`,children:(0,I.jsxs)(`div`,{className:`flex min-w-0 items-center gap-3`,children:[n?(0,I.jsx)(`img`,{src:n,alt:``,className:`welcome-brand-mark h-11 w-11 rounded-xl object-contain`}):(0,I.jsx)(`span`,{className:`welcome-brand-mark flex h-11 w-11 items-center justify-center rounded-xl text-sm font-black`,style:{background:`var(--tpl-panel)`,color:`var(--tpl-text)`},children:`AI+`}),(0,I.jsxs)(`div`,{className:`min-w-0`,children:[(0,I.jsx)(`div`,{className:`truncate text-sm font-black tracking-wide sm:text-base`,style:{color:`var(--tpl-text)`},children:t}),(0,I.jsx)(`div`,{className:`truncate text-xs font-medium`,style:{color:`var(--tpl-muted)`},children:i.label})]})]})}),i.composition&&i.composition!==`split`?(0,I.jsx)(We,{template:i,onPrimaryAction:r}):(0,I.jsxs)(`section`,{className:`grid flex-1 items-center gap-9 py-10 lg:grid-cols-[minmax(0,1fr)_minmax(390px,520px)] lg:gap-14 lg:py-12`,children:[(0,I.jsxs)(`div`,{className:`max-w-3xl`,children:[(0,I.jsxs)(`div`,{className:`welcome-badge mb-5 inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-bold`,style:{color:`var(--tpl-muted)`},children:[(0,I.jsx)(a,{size:14}),(0,I.jsx)(`span`,{children:i.name})]}),(0,I.jsx)(`h1`,{className:`welcome-title-gradient m-0 max-w-3xl text-4xl font-black leading-[1.06] tracking-normal sm:text-5xl lg:text-6xl`,children:i.headline}),(0,I.jsx)(`p`,{className:`mt-5 max-w-2xl text-base leading-8 sm:text-lg`,style:{color:`var(--tpl-muted)`},children:i.subline}),(0,I.jsxs)(`div`,{className:`mt-8 flex flex-col gap-3 sm:flex-row sm:items-center`,children:[(0,I.jsx)(Z,{onPrimaryAction:r}),(0,I.jsx)(`div`,{className:`flex flex-wrap gap-2`,children:i.chips.map(e=>(0,I.jsx)(`span`,{className:`welcome-chip rounded-full px-3 py-1.5 text-xs font-bold`,style:{color:`var(--tpl-muted)`},children:e},e))})]}),(0,I.jsx)(`div`,{className:`mt-10 grid max-w-xl grid-cols-3 gap-3`,children:i.metrics.map(e=>(0,I.jsxs)(`div`,{className:`welcome-metric rounded-2xl p-4`,children:[(0,I.jsx)(`div`,{className:`text-xl font-black sm:text-2xl`,style:{color:`var(--tpl-text)`},children:e.value}),(0,I.jsx)(`div`,{className:`mt-1 text-xs font-medium`,style:{color:`var(--tpl-muted)`},children:e.label})]},e.label))})]}),(0,I.jsx)(Be,{template:i})]})]})]})}function qe(){let[e,t]=(0,F.useState)(!1),[n,r]=(0,F.useState)(`KULAAI`),[i,a]=(0,F.useState)(``),[o]=(0,F.useState)(()=>Y());return(0,F.useEffect)(()=>{let e=!0;return Oe().then(t=>{e&&(r(t.siteName||`KULAAI`),a(t.siteIcon||``))}),()=>{e=!1}},[]),(0,I.jsxs)(I.Fragment,{children:[(0,I.jsx)(Ke,{templateId:o,siteName:n,siteIcon:i,onPrimaryAction:()=>t(!0)}),(0,I.jsx)(K,{open:e,onClose:()=>t(!1),defaultTab:`login`,onSuccess:()=>{},siteName:n,siteIcon:i})]})}var Je=(0,F.lazy)(()=>m(()=>import(`./page-BV-cLHa8.js`),__vite__mapDeps([0,1,2,3,4,5,6,7,8,9,10]))),Ye=(0,F.lazy)(()=>m(()=>import(`./page-DQYTx3-_.js`),__vite__mapDeps([11,1,2,3,4,10,7,8,9]))),Xe=(0,F.lazy)(()=>m(()=>import(`./page-CUhktpCV.js`),__vite__mapDeps([12,1,2,3,4,6,7,8,9,10]))),Ze=(0,F.lazy)(()=>m(()=>import(`./page-Cg-SMgJi.js`),__vite__mapDeps([13,1,2,3,10,9]))),Qe=(0,F.lazy)(()=>m(()=>import(`./page-Cnm5dfWg.js`),__vite__mapDeps([14,1,2,3,10,7,8,9]))),$e=(0,F.lazy)(()=>m(()=>import(`./page-CdVDJWlX.js`),__vite__mapDeps([15,1,2,3,10,7,8,9]))),et=(0,F.lazy)(()=>m(()=>import(`./page-B5yZ0BqV.js`),__vite__mapDeps([16,1,2,3,10,7,8,9]))),tt=(0,F.lazy)(()=>m(()=>import(`./page-M6-UOEJj.js`),__vite__mapDeps([17,1,2,3,10,7,8,9]))),nt=(0,F.lazy)(()=>m(()=>import(`./page-DJ_KFirf.js`),__vite__mapDeps([18,1,2,3,10,7,8,9]))),rt=(0,F.lazy)(()=>m(()=>import(`./page-DcoFF2I1.js`),__vite__mapDeps([19,1,2,3,10,7,8,9]))),it=(0,F.lazy)(()=>m(()=>import(`./square-C3LlLvwm.js`),__vite__mapDeps([20,1,2,3,10,7,8,9]))),at=(0,F.lazy)(()=>m(()=>import(`./page-_4e3AbXN.js`),__vite__mapDeps([21,1,2,3,10,7,8,9]))),ot=(0,F.lazy)(()=>m(()=>import(`./page-BqTy5xl5.js`),__vite__mapDeps([22,1,2,3,10,7,8,9]))),st=(0,F.lazy)(()=>m(()=>import(`./tag-DtxqVX68.js`),__vite__mapDeps([23,1,2,3,10,7,8,9]))),ct=(0,F.lazy)(()=>m(()=>import(`./news-CEYk7MLf.js`),__vite__mapDeps([24,1,2,3,10,7,8,9]))),lt=(0,F.lazy)(()=>m(()=>import(`./page-DA9ndLYC.js`),__vite__mapDeps([25,1,2,3,5,10,7,8,9]))),ut=(0,F.lazy)(()=>m(()=>import(`./page-BDhjbMeJ.js`),__vite__mapDeps([26,1,2,3,10,7,8,9]))),dt=(0,F.lazy)(()=>m(()=>import(`./page-DTQf2uI8.js`),__vite__mapDeps([27,1,2,3,10]))),ft=(0,F.lazy)(()=>m(()=>import(`./page-CI2rFovR.js`),__vite__mapDeps([28,1,2,3,10]))),pt=(0,F.lazy)(()=>m(()=>import(`./page-BT2RIqxS.js`),__vite__mapDeps([29,1,2,3,10]))),mt=(0,F.lazy)(()=>m(()=>import(`./page-fzkb2HJA.js`),__vite__mapDeps([30,1,2,3,10,7,8,9]))),ht=(0,F.lazy)(()=>m(()=>import(`./page-CI48SGlV.js`),__vite__mapDeps([31,1,2,3,10,7,8,9]))),gt=(0,F.lazy)(()=>m(()=>import(`./page-DEZ5Uxjr.js`),__vite__mapDeps([32,1,2,3,10,7,8,9]))),_t=`https://api.877ai.cn/api`,vt=new Set([`/`,`/videocomic`,`/pricing`,`/free-vip`,`/group-buy`,`/news`,`/terms`,`/privacy`,`/feedback`,`/payment/success`,`/payment/qr`,`/payment/jsapi`]),yt=[`/group-buy/`,`/news/tag/`,`/news/`,`/share/`];function bt(e){return e.length>1&&e.endsWith(`/`)?e.slice(0,-1):e}function xt(e){let t=bt(e);return vt.has(t)||yt.some(e=>t.startsWith(e))}function St(){let e=window.location.hostname;if(/^\d+\.\d+\.\d+\.\d+$/.test(e)||e===`localhost`)return null;let t=e.split(`.`);return t.length>=3&&t[0]!==`www`?t[0]:null}async function Ct(){if(new URLSearchParams(window.location.search).get(`ref`)?.replace(/\/+$/,``))return;try{let e=window.location.host,t=await fetch(`${_t}/auth/resolve-host?host=${encodeURIComponent(e)}`);if(t.ok){let e=await t.json();if(e?.inviteCode){A(`kulaai_agent_ref`,e.inviteCode);return}}}catch{}let e=St();if(e)try{let t=await fetch(`${_t}/auth/resolve-subdomain?subdomain=${encodeURIComponent(e)}`);if(t.ok){let e=await t.json();e?.inviteCode&&A(`kulaai_agent_ref`,e.inviteCode)}}catch{}}function wt(){let e=ie(),t=!M()&&!xt(e.pathname);return(0,F.useEffect)(()=>{Ct()},[]),(0,F.useEffect)(()=>{let e=new URLSearchParams(window.location.search).get(`ref`)?.replace(/\/+$/,``);e&&A(`kulaai_agent_ref`,e)},[e.search]),(0,F.useEffect)(()=>{fetch(`${_t}/tracking/pageview`,{method:`POST`,headers:{"Content-Type":`application/json`},body:JSON.stringify({path:e.pathname,host:window.location.host})}).catch(()=>{})},[e.pathname]),(0,I.jsx)(G,{children:t?(0,I.jsx)(qe,{},`${e.pathname}${e.search}`):(0,I.jsx)(F.Suspense,{fallback:(0,I.jsx)(`div`,{className:`h-screen w-screen bg-background`}),children:(0,I.jsxs)(a,{children:[(0,I.jsx)(s,{path:`/`,element:(0,I.jsx)(Je,{})}),(0,I.jsx)(s,{path:`/login`,element:(0,I.jsx)(b,{to:`/`,replace:!0})}),(0,I.jsx)(s,{path:`/register`,element:(0,I.jsx)(b,{to:`/`,replace:!0})}),(0,I.jsx)(s,{path:`/pricing`,element:(0,I.jsx)(Ye,{})}),(0,I.jsx)(s,{path:`/account`,element:(0,I.jsx)(Xe,{})}),(0,I.jsx)(s,{path:`/settings`,element:(0,I.jsx)(Ze,{})}),(0,I.jsx)(s,{path:`/feedback`,element:(0,I.jsx)(Qe,{})}),(0,I.jsx)(s,{path:`/free-vip`,element:(0,I.jsx)($e,{})}),(0,I.jsx)(s,{path:`/payment/success`,element:(0,I.jsx)(et,{})}),(0,I.jsx)(s,{path:`/payment/qr`,element:(0,I.jsx)(tt,{})}),(0,I.jsx)(s,{path:`/payment/jsapi`,element:(0,I.jsx)(nt,{})}),(0,I.jsx)(s,{path:`/group-buy`,element:(0,I.jsx)(it,{})}),(0,I.jsx)(s,{path:`/group-buy/:id`,element:(0,I.jsx)(rt,{})}),(0,I.jsx)(s,{path:`/agent`,element:(0,I.jsx)(at,{})}),(0,I.jsx)(s,{path:`/news`,element:(0,I.jsx)(ct,{})}),(0,I.jsx)(s,{path:`/news/tag/:tag`,element:(0,I.jsx)(st,{})}),(0,I.jsx)(s,{path:`/news/:slug`,element:(0,I.jsx)(ot,{})}),(0,I.jsx)(s,{path:`/share/:token`,element:(0,I.jsx)(lt,{})}),(0,I.jsx)(s,{path:`/creator/:id`,element:(0,I.jsx)(ut,{})}),(0,I.jsx)(s,{path:`/terms`,element:(0,I.jsx)(ft,{})}),(0,I.jsx)(s,{path:`/privacy`,element:(0,I.jsx)(pt,{})}),(0,I.jsx)(s,{path:`/videocomic`,element:(0,I.jsx)(mt,{})}),(0,I.jsx)(s,{path:`/orders`,element:(0,I.jsx)(ht,{})}),(0,I.jsx)(s,{path:`/invoices`,element:(0,I.jsx)(gt,{})}),(0,I.jsx)(s,{path:`*`,element:(0,I.jsx)(dt,{})})]})})})}`serviceWorker`in navigator&&window.addEventListener(`load`,()=>{navigator.serviceWorker.register(`/sw.js`).catch(()=>{})}),(0,P.createRoot)(document.getElementById(`root`)).render((0,I.jsx)(Se,{children:(0,I.jsx)(r,{children:(0,I.jsx)(W,{children:(0,I.jsx)(Ne,{children:(0,I.jsx)(H,{children:(0,I.jsx)(wt,{})})})})})}));export{U as n,je as r,K as t};