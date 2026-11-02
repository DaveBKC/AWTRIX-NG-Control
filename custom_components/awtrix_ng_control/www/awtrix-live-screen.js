/* AWTRIX Live Screen v1.1.6 — crisp LED matrix renderer, AWTRIX 3 and NG. */
class AwtrixLiveScreenCard extends HTMLElement {
  setConfig(config) {
    if (!config.prefix || !/^[A-Za-z0-9_-]{1,64}$/.test(config.prefix)) throw Error('Set prefix (MQTT prefix)');
    if (!['awtrix3', 'awtrix_ng'].includes(config.firmware)) throw Error('firmware must be awtrix3 or awtrix_ng');
    this._config = {...config};
    if (!this.shadowRoot) {
      this.attachShadow({mode: 'open'});
      this.shadowRoot.innerHTML = `<style>
        :host{display:block;min-width:0}
        ha-card{--accent:#50c9ed;position:relative;overflow:hidden;background:linear-gradient(145deg,var(--ha-card-background,var(--card-background-color,#1d2430)) 0%,var(--ha-card-background,var(--card-background-color,#1d2430)) 100%);border:1px solid var(--divider-color,rgba(140,160,184,.18));border-radius:18px;padding:17px 18px 15px;box-sizing:border-box;box-shadow:0 7px 24px rgba(0,0,0,.07)}
        .head{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:14px;min-width:0}
        .identity{display:flex;align-items:center;gap:10px;min-width:0}
        .device-icon{display:grid;place-items:center;width:36px;height:36px;border-radius:11px;background:color-mix(in srgb,var(--accent) 13%,transparent);color:var(--accent);flex-shrink:0}
        .device-icon svg{width:19px;height:19px;stroke:currentColor;fill:none;stroke-width:1.8}
        .heading{min-width:0}.title{font-size:14px;font-weight:650;letter-spacing:.1px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--primary-text-color)}
        .subtitle{font-size:11px;color:var(--secondary-text-color);margin-top:3px}
        .live{display:flex;align-items:center;gap:6px;font-size:10px;font-weight:750;letter-spacing:1px;color:var(--secondary-text-color);padding:6px 9px;background:var(--secondary-background-color,rgba(120,130,150,.08));border-radius:999px;flex-shrink:0}
        .dot{width:7px;height:7px;border-radius:50%;background:#858e9e;box-shadow:none}
        .live.connected .dot{background:#27bd81;box-shadow:0 0 0 3px rgba(39,189,129,.13)}
        .device{padding:9px;background:linear-gradient(155deg,#222c37,#0e141d 66%);border:1px solid #3b4857;border-radius:15px;box-shadow:inset 0 1px 0 rgba(255,255,255,.13),0 7px 15px rgba(0,0,0,.20)}
        .display{position:relative;background:#000;border:2px solid #05080d;border-radius:7px;padding:7px;box-shadow:inset 0 0 15px rgba(0,0,0,.7),0 0 0 1px #3b4350;overflow:hidden}
        canvas{display:block;width:100%;height:auto;image-rendering:pixelated;background:#000;border-radius:1px}
        .foot{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:12px;color:var(--secondary-text-color);font-size:11px}
        .status{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:70%;text-align:right}
        .version{font-size:10px;font-weight:700;letter-spacing:.7px;color:var(--secondary-text-color)}
        @media(max-width:340px){ha-card{padding:12px}.display{padding:5px}}
      </style><ha-card>
        <div class="head"><div class="identity"><span class="device-icon"><svg viewBox="0 0 24 24"><rect x="2.5" y="5" width="19" height="14" rx="3"/><path d="M6 9h12M6 13h12"/></svg></span><div class="heading"><div class="title"></div><div class="subtitle"></div></div></div><div class="live"><span class="dot"></span><span class="live-label">OFFLINE</span></div></div>
        <div class="device"><div class="display"><canvas width="52" height="16"></canvas></div></div>
        <div class="foot"><span class="version"></span><span class="status">Connecting…</span></div>
      </ha-card>`;
    }
    this.shadowRoot.querySelector('.title').textContent = config.title || config.prefix;
    this.shadowRoot.querySelector('.subtitle').textContent = config.firmware === 'awtrix3' ? 'AWTRIX 3 · 32 × 8' : 'AWTRIX NG · 52 × 16';
    this.shadowRoot.querySelector('.version').textContent = config.prefix.toUpperCase();
    const canvas = this.shadowRoot.querySelector('canvas');
    this._ledScale = 8;
    canvas.width = (config.firmware === 'awtrix3' ? 32 : 52) * this._ledScale;
    canvas.height = (config.firmware === 'awtrix3' ? 8 : 16) * this._ledScale;
    this._ctx = canvas.getContext('2d', {alpha: false});
    this._ctx.imageSmoothingEnabled = false;
    this._ctx.fillStyle='#000';this._ctx.fillRect(0,0,canvas.width,canvas.height);
    this._restart();
  }
  set hass(hass) { this._hass = hass; this._restart(); }
  connectedCallback() { this._connected = true; this._restart(); }
  disconnectedCallback() { this._connected = false; this._disconnect(); }
  _status(s) {
    const root=this.shadowRoot; if(!root)return;
    const el=root.querySelector('.status');if(el)el.textContent=s;
    const live=root.querySelector('.live');const label=root.querySelector('.live-label');
    const active=s==='Streaming screen';
    live?.classList.toggle('connected',active);if(label)label.textContent=active?'LIVE':'WAITING';
  }
  _disconnect() { const unsub=this._unsub;this._unsub=null;this._starting=false;this._sessionKey=null;if(unsub) Promise.resolve(unsub).then(fn=>fn?.()).catch(()=>{}); }
  async _restart() {
    if (!this._connected || !this._hass || !this._config || !this._ctx) return;
    const key=this._config.prefix+'/'+this._config.firmware;
    if (this._sessionKey === key) return;
    this._disconnect(); this._receivedFrame=false; this._sessionKey=key;
    const generation = (this._generation=(this._generation||0)+1);
    this._status('Connecting…');
    try {
      const unsub=await this._hass.connection.subscribeMessage(frame=>{
        if(generation!==this._generation)return;
        const {width:w,height:h,pixels:px}=frame||{};
        if(!Number.isInteger(w)||!Number.isInteger(h)||w*h>4096||!Array.isArray(px)||px.length!==w*h)return;
        const canvas=this.shadowRoot.querySelector('canvas');
        const S=this._ledScale;
        if(canvas.width!==w*S||canvas.height!==h*S){
          canvas.width=w*S;canvas.height=h*S;
          this._ctx.imageSmoothingEnabled=false;
        }
        // Render each source pixel as a distinct LED with a 1-unit dark gutter.
        // Drawing at 8x native resolution preserves the LED grid on both panels.
        this._ctx.fillStyle='#080b0f';
        this._ctx.fillRect(0,0,canvas.width,canvas.height);
        for(let i=0;i<px.length;i++){
          const c=Number(px[i])>>>0;
          const x=(i%w)*S, y=Math.floor(i/w)*S;
          const r=(c>>16)&255, g=(c>>8)&255, b=c&255;
          this._ctx.fillStyle=`rgb(${r},${g},${b})`;
          this._ctx.fillRect(x+1,y+1,S-2,S-2);
        }
        this._receivedFrame=true;this._status('Streaming screen');
      },{type:'awtrix_ng_control/live_screen',prefix:this._config.prefix,firmware:this._config.firmware});
      if(generation!==this._generation||!this._connected){unsub();return;}
      this._unsub=unsub;
      if(!this._receivedFrame)this._status('In attesa del display…');
    } catch(e){if(generation===this._generation){this._status('Error: '+String(e.message||e));this._sessionKey=null;}}
  }
  getCardSize(){return 3;}
  static getStubConfig(){return {prefix:'tc002',firmware:'awtrix_ng',title:'AWTRIX Live Screen'};}
}
customElements.define('awtrix-live-screen-card',AwtrixLiveScreenCard);
window.customCards=window.customCards||[];
window.customCards.push({type:'awtrix-live-screen-card',name:'AWTRIX Live Screen',description:'Live MQTT screen mirror for AWTRIX 3 and NG'});
