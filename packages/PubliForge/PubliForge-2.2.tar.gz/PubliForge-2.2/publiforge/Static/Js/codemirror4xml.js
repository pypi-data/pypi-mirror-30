/* CodeMirror - Minified & Bundled
   Generated on 28/06/2016 with http://codemirror.net/doc/compress.html
   Version: 5.16.0

   Modes:
   - xml.js
   Add-ons:
   - closetag.js
   - show-hint.js
   - xml-hint.js
 */

!function(a){"object"==typeof exports&&"object"==typeof module?a(require("../../lib/codemirror")):"function"==typeof define&&define.amd?define(["../../lib/codemirror"],a):a(CodeMirror)}(function(a){"use strict";var b={autoSelfClosers:{area:!0,base:!0,br:!0,col:!0,command:!0,embed:!0,frame:!0,hr:!0,img:!0,input:!0,keygen:!0,link:!0,meta:!0,param:!0,source:!0,track:!0,wbr:!0,menuitem:!0},implicitlyClosed:{dd:!0,li:!0,optgroup:!0,option:!0,p:!0,rp:!0,rt:!0,tbody:!0,td:!0,tfoot:!0,th:!0,tr:!0},contextGrabbers:{dd:{dd:!0,dt:!0},dt:{dd:!0,dt:!0},li:{li:!0},option:{option:!0,optgroup:!0},optgroup:{optgroup:!0},p:{address:!0,article:!0,aside:!0,blockquote:!0,dir:!0,div:!0,dl:!0,fieldset:!0,footer:!0,form:!0,h1:!0,h2:!0,h3:!0,h4:!0,h5:!0,h6:!0,header:!0,hgroup:!0,hr:!0,menu:!0,nav:!0,ol:!0,p:!0,pre:!0,section:!0,table:!0,ul:!0},rp:{rp:!0,rt:!0},rt:{rp:!0,rt:!0},tbody:{tbody:!0,tfoot:!0},td:{td:!0,th:!0},tfoot:{tbody:!0},th:{td:!0,th:!0},thead:{tbody:!0,tfoot:!0},tr:{tr:!0}},doNotIndent:{pre:!0},allowUnquoted:!0,allowMissing:!0,caseFold:!0},c={autoSelfClosers:{},implicitlyClosed:{},contextGrabbers:{},doNotIndent:{},allowUnquoted:!1,allowMissing:!1,caseFold:!1};a.defineMode("xml",function(d,e){function l(a,b){function c(c){return b.tokenize=c,c(a,b)}var d=a.next();if("<"==d)return a.eat("!")?a.eat("[")?a.match("CDATA[")?c(o("atom","]]>")):null:a.match("--")?c(o("comment","-->")):a.match("DOCTYPE",!0,!0)?(a.eatWhile(/[\w\._\-]/),c(p(1))):null:a.eat("?")?(a.eatWhile(/[\w\._\-]/),b.tokenize=o("meta","?>"),"meta"):(j=a.eat("/")?"closeTag":"openTag",b.tokenize=m,"tag bracket");if("&"==d){var e;return e=a.eat("#")?a.eat("x")?a.eatWhile(/[a-fA-F\d]/)&&a.eat(";"):a.eatWhile(/[\d]/)&&a.eat(";"):a.eatWhile(/[\w\.\-:]/)&&a.eat(";"),e?"atom":"error"}return a.eatWhile(/[^&<]/),null}function m(a,b){var c=a.next();if(">"==c||"/"==c&&a.eat(">"))return b.tokenize=l,j=">"==c?"endTag":"selfcloseTag","tag bracket";if("="==c)return j="equals",null;if("<"==c){b.tokenize=l,b.state=t,b.tagName=b.tagStart=null;var d=b.tokenize(a,b);return d?d+" tag error":"tag error"}return/[\'\"]/.test(c)?(b.tokenize=n(c),b.stringStartCol=a.column(),b.tokenize(a,b)):(a.match(/^[^\s\u00a0=<>\"\']*[^\s\u00a0=<>\"\'\/]/),"word")}function n(a){var b=function(b,c){for(;!b.eol();)if(b.next()==a){c.tokenize=m;break}return"string"};return b.isInAttribute=!0,b}function o(a,b){return function(c,d){for(;!c.eol();){if(c.match(b)){d.tokenize=l;break}c.next()}return a}}function p(a){return function(b,c){for(var d;null!=(d=b.next());){if("<"==d)return c.tokenize=p(a+1),c.tokenize(b,c);if(">"==d){if(1==a){c.tokenize=l;break}return c.tokenize=p(a-1),c.tokenize(b,c)}}return"meta"}}function q(a,b,c){this.prev=a.context,this.tagName=b,this.indent=a.indented,this.startOfLine=c,(g.doNotIndent.hasOwnProperty(b)||a.context&&a.context.noIndent)&&(this.noIndent=!0)}function r(a){a.context&&(a.context=a.context.prev)}function s(a,b){for(var c;;){if(!a.context)return;if(c=a.context.tagName,!g.contextGrabbers.hasOwnProperty(c)||!g.contextGrabbers[c].hasOwnProperty(b))return;r(a)}}function t(a,b,c){return"openTag"==a?(c.tagStart=b.column(),u):"closeTag"==a?v:t}function u(a,b,c){return"word"==a?(c.tagName=b.current(),k="tag",y):(k="error",u)}function v(a,b,c){if("word"==a){var d=b.current();return c.context&&c.context.tagName!=d&&g.implicitlyClosed.hasOwnProperty(c.context.tagName)&&r(c),c.context&&c.context.tagName==d||g.matchClosing===!1?(k="tag",w):(k="tag error",x)}return k="error",x}function w(a,b,c){return"endTag"!=a?(k="error",w):(r(c),t)}function x(a,b,c){return k="error",w(a,b,c)}function y(a,b,c){if("word"==a)return k="attribute",z;if("endTag"==a||"selfcloseTag"==a){var d=c.tagName,e=c.tagStart;return c.tagName=c.tagStart=null,"selfcloseTag"==a||g.autoSelfClosers.hasOwnProperty(d)?s(c,d):(s(c,d),c.context=new q(c,d,e==c.indented)),t}return k="error",y}function z(a,b,c){return"equals"==a?A:(g.allowMissing||(k="error"),y(a,b,c))}function A(a,b,c){return"string"==a?B:"word"==a&&g.allowUnquoted?(k="string",y):(k="error",y(a,b,c))}function B(a,b,c){return"string"==a?B:y(a,b,c)}var f=d.indentUnit,g={},h=e.htmlMode?b:c;for(var i in h)g[i]=h[i];for(var i in e)g[i]=e[i];var j,k;return l.isInText=!0,{startState:function(a){var b={tokenize:l,state:t,indented:a||0,tagName:null,tagStart:null,context:null};return null!=a&&(b.baseIndent=a),b},token:function(a,b){if(!b.tagName&&a.sol()&&(b.indented=a.indentation()),a.eatSpace())return null;j=null;var c=b.tokenize(a,b);return(c||j)&&"comment"!=c&&(k=null,b.state=b.state(j||c,a,b),k&&(c="error"==k?c+" error":k)),c},indent:function(b,c,d){var e=b.context;if(b.tokenize.isInAttribute)return b.tagStart==b.indented?b.stringStartCol+1:b.indented+f;if(e&&e.noIndent)return a.Pass;if(b.tokenize!=m&&b.tokenize!=l)return d?d.match(/^(\s*)/)[0].length:0;if(b.tagName)return g.multilineTagIndentPastTag!==!1?b.tagStart+b.tagName.length+2:b.tagStart+f*(g.multilineTagIndentFactor||1);if(g.alignCDATA&&/<!\[CDATA\[/.test(c))return 0;var h=c&&/^<(\/)?([\w_:\.-]*)/.exec(c);if(h&&h[1])for(;e;){if(e.tagName==h[2]){e=e.prev;break}if(!g.implicitlyClosed.hasOwnProperty(e.tagName))break;e=e.prev}else if(h)for(;e;){var i=g.contextGrabbers[e.tagName];if(!i||!i.hasOwnProperty(h[2]))break;e=e.prev}for(;e&&e.prev&&!e.startOfLine;)e=e.prev;return e?e.indent+f:b.baseIndent||0},electricInput:/<\/[\s\w:]+>$/,blockCommentStart:"<!--",blockCommentEnd:"-->",configuration:g.htmlMode?"html":"xml",helperType:g.htmlMode?"html":"xml",skipAttribute:function(a){a.state==A&&(a.state=y)}}}),a.defineMIME("text/xml","xml"),a.defineMIME("application/xml","xml"),a.mimeModes.hasOwnProperty("text/html")||a.defineMIME("text/html",{name:"xml",htmlMode:!0})}),function(a){"object"==typeof exports&&"object"==typeof module?a(require("../../lib/codemirror"),require("../fold/xml-fold")):"function"==typeof define&&define.amd?define(["../../lib/codemirror","../fold/xml-fold"],a):a(CodeMirror)}(function(a){function d(d){if(d.getOption("disableInput"))return a.Pass;for(var e=d.listSelections(),f=[],i=0;i<e.length;i++){if(!e[i].empty())return a.Pass;var j=e[i].head,k=d.getTokenAt(j),l=a.innerMode(d.getMode(),k.state),m=l.state;if("xml"!=l.mode.name||!m.tagName)return a.Pass;var n=d.getOption("autoCloseTags"),o="html"==l.mode.configuration,p="object"==typeof n&&n.dontCloseTags||o&&b,q="object"==typeof n&&n.indentTags||o&&c,r=m.tagName;k.end>j.ch&&(r=r.slice(0,r.length-k.end+j.ch));var s=r.toLowerCase();if(!r||"string"==k.type&&(k.end!=j.ch||!/[\"\']/.test(k.string.charAt(k.string.length-1))||1==k.string.length)||"tag"==k.type&&"closeTag"==m.type||k.string.indexOf("/")==k.string.length-1||p&&g(p,s)>-1||h(d,r,j,m,!0))return a.Pass;var t=q&&g(q,s)>-1;f[i]={indent:t,text:">"+(t?"\n\n":"")+"</"+r+">",newPos:t?a.Pos(j.line+1,0):a.Pos(j.line,j.ch+1)}}for(var i=e.length-1;i>=0;i--){var u=f[i];d.replaceRange(u.text,e[i].head,e[i].anchor,"+insert");var v=d.listSelections().slice(0);v[i]={head:u.newPos,anchor:u.newPos},d.setSelections(v),u.indent&&(d.indentLine(u.newPos.line,null,!0),d.indentLine(u.newPos.line+1,null,!0))}}function e(b,c){for(var d=b.listSelections(),e=[],f=c?"/":"</",g=0;g<d.length;g++){if(!d[g].empty())return a.Pass;var i=d[g].head,j=b.getTokenAt(i),k=a.innerMode(b.getMode(),j.state),l=k.state;if(c&&("string"==j.type||"<"!=j.string.charAt(0)||j.start!=i.ch-1))return a.Pass;var m;if("xml"!=k.mode.name)if("htmlmixed"==b.getMode().name&&"javascript"==k.mode.name)m=f+"script";else{if("htmlmixed"!=b.getMode().name||"css"!=k.mode.name)return a.Pass;m=f+"style"}else{if(!l.context||!l.context.tagName||h(b,l.context.tagName,i,l))return a.Pass;m=f+l.context.tagName}">"!=b.getLine(i.line).charAt(j.end)&&(m+=">"),e[g]=m}b.replaceSelections(e),d=b.listSelections();for(var g=0;g<d.length;g++)(g==d.length-1||d[g].head.line<d[g+1].head.line)&&b.indentLine(d[g].head.line)}function f(b){return b.getOption("disableInput")?a.Pass:e(b,!0)}function g(a,b){if(a.indexOf)return a.indexOf(b);for(var c=0,d=a.length;d>c;++c)if(a[c]==b)return c;return-1}function h(b,c,d,e,f){if(!a.scanForClosingTag)return!1;var g=Math.min(b.lastLine()+1,d.line+500),h=a.scanForClosingTag(b,d,null,g);if(!h||h.tag!=c)return!1;for(var i=e.context,j=f?1:0;i&&i.tagName==c;i=i.prev)++j;d=h.to;for(var k=1;j>k;k++){var l=a.scanForClosingTag(b,d,null,g);if(!l||l.tag!=c)return!1;d=l.to}return!0}a.defineOption("autoCloseTags",!1,function(b,c,e){if(e!=a.Init&&e&&b.removeKeyMap("autoCloseTags"),c){var g={name:"autoCloseTags"};("object"!=typeof c||c.whenClosing)&&(g["'/'"]=function(a){return f(a)}),("object"!=typeof c||c.whenOpening)&&(g["'>'"]=function(a){return d(a)}),b.addKeyMap(g)}});var b=["area","base","br","col","command","embed","hr","img","input","keygen","link","meta","param","source","track","wbr"],c=["applet","blockquote","body","button","div","dl","fieldset","form","frameset","h1","h2","h3","h4","h5","h6","head","html","iframe","layer","legend","object","ol","p","select","table","ul"];a.commands.closeTag=function(a){return e(a)}}),function(a){"object"==typeof exports&&"object"==typeof module?a(require("../../lib/codemirror")):"function"==typeof define&&define.amd?define(["../../lib/codemirror"],a):a(CodeMirror)}(function(a){"use strict";function d(a,b){this.cm=a,this.options=b,this.widget=null,this.debounce=0,this.tick=0,this.startPos=this.cm.getCursor("start"),this.startLen=this.cm.getLine(this.startPos.line).length-this.cm.getSelection().length;var c=this;a.on("cursorActivity",this.activityFunc=function(){c.cursorActivity()})}function g(b,c){var d=a.cmpPos(c.from,b.from);return d>0&&b.to.ch-b.from.ch!=c.to.ch-c.from.ch}function h(a,b,c){var d=a.options.hintOptions,e={};for(var f in p)e[f]=p[f];if(d)for(var f in d)void 0!==d[f]&&(e[f]=d[f]);if(c)for(var f in c)void 0!==c[f]&&(e[f]=c[f]);return e.hint.resolve&&(e.hint=e.hint.resolve(a,b)),e}function i(a){return"string"==typeof a?a:a.text}function j(a,b){function f(a,d){var f;f="string"!=typeof d?function(a){return d(a,b)}:c.hasOwnProperty(d)?c[d]:d,e[a]=f}var c={Up:function(){b.moveFocus(-1)},Down:function(){b.moveFocus(1)},PageUp:function(){b.moveFocus(-b.menuSize()+1,!0)},PageDown:function(){b.moveFocus(b.menuSize()-1,!0)},Home:function(){b.setFocus(0)},End:function(){b.setFocus(b.length-1)},Enter:b.pick,Tab:b.pick,Esc:b.close},d=a.options.customKeys,e=d?{}:c;if(d)for(var g in d)d.hasOwnProperty(g)&&f(g,d[g]);var h=a.options.extraKeys;if(h)for(var g in h)h.hasOwnProperty(g)&&f(g,h[g]);return e}function k(a,b){for(;b&&b!=a;){if("LI"===b.nodeName.toUpperCase()&&b.parentNode==a)return b;b=b.parentNode}}function l(d,e){this.completion=d,this.data=e,this.picked=!1;var f=this,g=d.cm,h=this.hints=document.createElement("ul");h.className="CodeMirror-hints",this.selectedHint=e.selectedHint||0;for(var l=e.list,m=0;m<l.length;++m){var n=h.appendChild(document.createElement("li")),o=l[m],p=b+(m!=this.selectedHint?"":" "+c);null!=o.className&&(p=o.className+" "+p),n.className=p,o.render?o.render(n,e,o):n.appendChild(document.createTextNode(o.displayText||i(o))),n.hintId=m}var q=g.cursorCoords(d.options.alignWithWord?e.from:null),r=q.left,s=q.bottom,t=!0;h.style.left=r+"px",h.style.top=s+"px";var u=window.innerWidth||Math.max(document.body.offsetWidth,document.documentElement.offsetWidth),v=window.innerHeight||Math.max(document.body.offsetHeight,document.documentElement.offsetHeight);(d.options.container||document.body).appendChild(h);var w=h.getBoundingClientRect(),x=w.bottom-v,y=h.scrollHeight>h.clientHeight+1;if(x>0){var z=w.bottom-w.top,A=q.top-(q.bottom-w.top);if(A-z>0)h.style.top=(s=q.top-z)+"px",t=!1;else if(z>v){h.style.height=v-5+"px",h.style.top=(s=q.bottom-w.top)+"px";var B=g.getCursor();e.from.ch!=B.ch&&(q=g.cursorCoords(B),h.style.left=(r=q.left)+"px",w=h.getBoundingClientRect())}}var C=w.right-u;if(C>0&&(w.right-w.left>u&&(h.style.width=u-5+"px",C-=w.right-w.left-u),h.style.left=(r=q.left-C)+"px"),y)for(var D=h.firstChild;D;D=D.nextSibling)D.style.paddingRight=g.display.nativeBarWidth+"px";if(g.addKeyMap(this.keyMap=j(d,{moveFocus:function(a,b){f.changeActive(f.selectedHint+a,b)},setFocus:function(a){f.changeActive(a)},menuSize:function(){return f.screenAmount()},length:l.length,close:function(){d.close()},pick:function(){f.pick()},data:e})),d.options.closeOnUnfocus){var E;g.on("blur",this.onBlur=function(){E=setTimeout(function(){d.close()},100)}),g.on("focus",this.onFocus=function(){clearTimeout(E)})}var F=g.getScrollInfo();return g.on("scroll",this.onScroll=function(){var a=g.getScrollInfo(),b=g.getWrapperElement().getBoundingClientRect(),c=s+F.top-a.top,e=c-(window.pageYOffset||(document.documentElement||document.body).scrollTop);return t||(e+=h.offsetHeight),e<=b.top||e>=b.bottom?d.close():(h.style.top=c+"px",void(h.style.left=r+F.left-a.left+"px"))}),a.on(h,"dblclick",function(a){var b=k(h,a.target||a.srcElement);b&&null!=b.hintId&&(f.changeActive(b.hintId),f.pick())}),a.on(h,"click",function(a){var b=k(h,a.target||a.srcElement);b&&null!=b.hintId&&(f.changeActive(b.hintId),d.options.completeOnSingleClick&&f.pick())}),a.on(h,"mousedown",function(){setTimeout(function(){g.focus()},20)}),a.signal(e,"select",l[0],h.firstChild),!0}function m(a,b){if(!a.somethingSelected())return b;for(var c=[],d=0;d<b.length;d++)b[d].supportsSelection&&c.push(b[d]);return c}function n(a,b,c,d){if(a.async)a(b,d,c);else{var e=a(b,c);e&&e.then?e.then(d):d(e)}}function o(b,c){var e,d=b.getHelpers(c,"hint");if(d.length){var f=function(a,b,c){function f(d){return d==e.length?b(null):void n(e[d],a,c,function(a){a&&a.list.length>0?b(a):f(d+1)})}var e=m(a,d);f(0)};return f.async=!0,f.supportsSelection=!0,f}return(e=b.getHelper(b.getCursor(),"hintWords"))?function(b){return a.hint.fromList(b,{words:e})}:a.hint.anyword?function(b,c){return a.hint.anyword(b,c)}:function(){}}var b="CodeMirror-hint",c="CodeMirror-hint-active";a.showHint=function(a,b,c){if(!b)return a.showHint(c);c&&c.async&&(b.async=!0);var d={hint:b};if(c)for(var e in c)d[e]=c[e];return a.showHint(d)},a.defineExtension("showHint",function(b){b=h(this,this.getCursor("start"),b);var c=this.listSelections();if(!(c.length>1)){if(this.somethingSelected()){if(!b.hint.supportsSelection)return;for(var e=0;e<c.length;e++)if(c[e].head.line!=c[e].anchor.line)return}this.state.completionActive&&this.state.completionActive.close();var f=this.state.completionActive=new d(this,b);f.options.hint&&(a.signal(this,"startCompletion",this),f.update(!0))}});var e=window.requestAnimationFrame||function(a){return setTimeout(a,1e3/60)},f=window.cancelAnimationFrame||clearTimeout;d.prototype={close:function(){this.active()&&(this.cm.state.completionActive=null,this.tick=null,this.cm.off("cursorActivity",this.activityFunc),this.widget&&this.data&&a.signal(this.data,"close"),this.widget&&this.widget.close(),a.signal(this.cm,"endCompletion",this.cm))},active:function(){return this.cm.state.completionActive==this},pick:function(b,c){var d=b.list[c];d.hint?d.hint(this.cm,b,d):this.cm.replaceRange(i(d),d.from||b.from,d.to||b.to,"complete"),a.signal(b,"pick",d),this.close()},cursorActivity:function(){this.debounce&&(f(this.debounce),this.debounce=0);var a=this.cm.getCursor(),b=this.cm.getLine(a.line);if(a.line!=this.startPos.line||b.length-a.ch!=this.startLen-this.startPos.ch||a.ch<this.startPos.ch||this.cm.somethingSelected()||a.ch&&this.options.closeCharacters.test(b.charAt(a.ch-1)))this.close();else{var c=this;this.debounce=e(function(){c.update()}),this.widget&&this.widget.disable()}},update:function(a){if(null!=this.tick){var b=this,c=++this.tick;n(this.options.hint,this.cm,this.options,function(d){b.tick==c&&b.finishUpdate(d,a)})}},finishUpdate:function(b,c){this.data&&a.signal(this.data,"update");var d=this.widget&&this.widget.picked||c&&this.options.completeSingle;this.widget&&this.widget.close(),b&&this.data&&g(this.data,b)||(this.data=b,b&&b.list.length&&(d&&1==b.list.length?this.pick(b,0):(this.widget=new l(this,b),a.signal(b,"shown"))))}},l.prototype={close:function(){if(this.completion.widget==this){this.completion.widget=null,this.hints.parentNode.removeChild(this.hints),this.completion.cm.removeKeyMap(this.keyMap);var a=this.completion.cm;this.completion.options.closeOnUnfocus&&(a.off("blur",this.onBlur),a.off("focus",this.onFocus)),a.off("scroll",this.onScroll)}},disable:function(){this.completion.cm.removeKeyMap(this.keyMap);var a=this;this.keyMap={Enter:function(){a.picked=!0}},this.completion.cm.addKeyMap(this.keyMap)},pick:function(){this.completion.pick(this.data,this.selectedHint)},changeActive:function(b,d){if(b>=this.data.list.length?b=d?this.data.list.length-1:0:0>b&&(b=d?0:this.data.list.length-1),this.selectedHint!=b){var e=this.hints.childNodes[this.selectedHint];e.className=e.className.replace(" "+c,""),e=this.hints.childNodes[this.selectedHint=b],e.className+=" "+c,e.offsetTop<this.hints.scrollTop?this.hints.scrollTop=e.offsetTop-3:e.offsetTop+e.offsetHeight>this.hints.scrollTop+this.hints.clientHeight&&(this.hints.scrollTop=e.offsetTop+e.offsetHeight-this.hints.clientHeight+3),a.signal(this.data,"select",this.data.list[this.selectedHint],e)}},screenAmount:function(){return Math.floor(this.hints.clientHeight/this.hints.firstChild.offsetHeight)||1}},a.registerHelper("hint","auto",{resolve:o}),a.registerHelper("hint","fromList",function(b,c){var d=b.getCursor(),e=b.getTokenAt(d),f=a.Pos(d.line,e.end);if(e.string&&/\w/.test(e.string[e.string.length-1]))var g=e.string,h=a.Pos(d.line,e.start);else var g="",h=f;for(var i=[],j=0;j<c.words.length;j++){var k=c.words[j];k.slice(0,g.length)==g&&i.push(k)}return i.length?{list:i,from:h,to:f}:void 0}),a.commands.autocomplete=a.showHint;var p={hint:a.hint.auto,completeSingle:!0,alignWithWord:!0,closeCharacters:/[\s()\[\]{};:>,]/,closeOnUnfocus:!0,completeOnSingleClick:!0,container:null,customKeys:null,extraKeys:null};a.defineOption("hintOptions",null)}),function(a){"object"==typeof exports&&"object"==typeof module?a(require("../../lib/codemirror")):"function"==typeof define&&define.amd?define(["../../lib/codemirror"],a):a(CodeMirror)}(function(a){"use strict";function c(c,d){var e=d&&d.schemaInfo,f=d&&d.quoteChar||'"';if(e){var g=c.getCursor(),h=c.getTokenAt(g);h.end>g.ch&&(h.end=g.ch,h.string=h.string.slice(0,g.ch-h.start));var i=a.innerMode(c.getMode(),h.state);if("xml"==i.mode.name){var l,o,j=[],k=!1,m=/\btag\b/.test(h.type)&&!/>$/.test(h.string),n=m&&/^\w/.test(h.string);if(n){var p=c.getLine(g.line).slice(Math.max(0,h.start-2),h.start),q=/<\/$/.test(p)?"close":/<$/.test(p)?"open":null;q&&(o=h.start-("close"==q?2:1))}else m&&"<"==h.string?q="open":m&&"</"==h.string&&(q="close");if(!m&&!i.state.tagName||q){n&&(l=h.string),k=q;var r=i.state.context,s=r&&e[r.tagName],t=r?s&&s.children:e["!top"];if(t&&"close"!=q)for(var u=0;u<t.length;++u)l&&0!=t[u].lastIndexOf(l,0)||j.push("<"+t[u]);else if("close"!=q)for(var v in e)!e.hasOwnProperty(v)||"!top"==v||"!attrs"==v||l&&0!=v.lastIndexOf(l,0)||j.push("<"+v);r&&(!l||"close"==q&&0==r.tagName.lastIndexOf(l,0))&&j.push("</"+r.tagName+">")}else{var s=e[i.state.tagName],w=s&&s.attrs,x=e["!attrs"];if(!w&&!x)return;if(w){if(x){var y={};for(var z in x)x.hasOwnProperty(z)&&(y[z]=x[z]);for(var z in w)w.hasOwnProperty(z)&&(y[z]=w[z]);w=y}}else w=x;if("string"==h.type||"="==h.string){var B,p=c.getRange(b(g.line,Math.max(0,g.ch-60)),b(g.line,"string"==h.type?h.start:h.end)),A=p.match(/([^\s\u00a0=<>\"\']+)=$/);if(!A||!w.hasOwnProperty(A[1])||!(B=w[A[1]]))return;if("function"==typeof B&&(B=B.call(this,c)),"string"==h.type){l=h.string;var C=0;/['"]/.test(h.string.charAt(0))&&(f=h.string.charAt(0),l=h.string.slice(1),C++);var D=h.string.length;/['"]/.test(h.string.charAt(D-1))&&(f=h.string.charAt(D-1),l=h.string.substr(C,D-2)),k=!0}for(var u=0;u<B.length;++u)l&&0!=B[u].lastIndexOf(l,0)||j.push(f+B[u]+f)}else{"attribute"==h.type&&(l=h.string,k=!0);for(var E in w)!w.hasOwnProperty(E)||l&&0!=E.lastIndexOf(l,0)||j.push(E)}}return{list:j,from:k?b(g.line,null==o?h.start:o):g,to:k?b(g.line,h.end):g}}}}var b=a.Pos;a.registerHelper("hint","xml",c)});


// ============================================================================


/*global jQuery: true */
/*global setTimeout: true */
/*global setInterval: true */
/*global CodeMirror: true */
/*global codemirrors: true */
/*global tags: true */

var i18n = {};
i18n.fr = {
    "Do you really want to quit the editor?": "Voulez-vous vraiment quitter l'éditeur ?"
};

// ----------------------------------------------------------------------------
function schema2tags(schema, top) {
    var tags = {"!top": top};
    var element;

    for (var pattern in schema) {
        if (pattern.indexOf(".") == 0)
            continue;
        element = schema[pattern].element || pattern;
        if (element.indexOf(".") != -1)
            continue;
        if (!tags[element])
            tags[element] = {};

        if (schema[pattern].attributes) {
            if (!tags[element].attrs)
                tags[element].attrs = schema[pattern].attributes;
            else
                jQuery.extend(tags[element].attrs, schema[pattern].attributes);
        }

        if (!tags[element].children)
            tags[element].children = [];
        if (!schema[pattern].content)
            continue;

        for (var i = 0 ; i < schema[pattern].content.length ; i++)
            for (var elt, j = 0; j < schema[pattern].content[i].length; j++) {
                elt = schema[schema[pattern].content[i][j]] &&
                    schema[schema[pattern].content[i][j]].element
                    || schema[pattern].content[i][j];
                if (elt.indexOf(".") == -1
                    && jQuery.inArray(elt, tags[element].children) == -1)
                    tags[element].children.push(elt);
            }
    }

    return tags;
}

// ----------------------------------------------------------------------------
function completeAfter(cm, pred) {
    var cur = cm.getCursor();
    if (!pred || pred()) setTimeout(function() {
        if (!cm.state.completionActive)
            CodeMirror.showHint(
                cm, CodeMirror.xmlHint,
                { schemaInfo: tags, completeSingle: false}
            );
    }, 100);
    return CodeMirror.Pass;
}

// ----------------------------------------------------------------------------
function completeIfAfterLt(cm) {
    return completeAfter(cm, function() {
        var cur = cm.getCursor();
        return cm.getRange(CodeMirror.Pos(cur.line, cur.ch - 1), cur) == "<";
    });
}

// ----------------------------------------------------------------------------
function completeIfInTag(cm) {
    return completeAfter(cm, function() {
        var tok = cm.getTokenAt(cm.getCursor());
        if (tok.type == "string"
            && (!/['"]/.test(tok.string.charAt(tok.string.length - 1))
                || tok.string.length == 1))
            return false;
        var inner = CodeMirror.innerMode(cm.getMode(), tok.state).state;
        return inner.tagName;
    });
}

// ----------------------------------------------------------------------------
// Hide empty fields in metadat table.
function metaHideEmptyFields($metaTable) {
    // Find empty fields
    var fields = [];
    $metaTable.find("input[type='text'], input[type='checkbox'], textarea, select")
        .each(function() {
            var $this = jQuery(this);
            if ((!jQuery.trim($this.val())
                 || ($this.attr('type') == 'checkbox' && !$this.prop('checked')))
                && !$this.next(".error").length) {
                var $tr = $this.parents("tr");
                fields.push([$tr.prevAll("tr").length, $tr.children("th").text()]);
                $tr.hide();
            }
        });
    if (!(fields.length))
        return;

    // Hide and connect
    var $newTag = "<option/>";
    for (var i = 0 ; i < fields.length ; i++)
        $newTag += "<option value='" + fields[i][0] + "'>"
        + fields[i][1] + "</option>";
    $newTag = jQuery(
        "<tr><td><select>"+$newTag+"</select></td><td colspan='2'/></tr>");
    $newTag.find("select").change(function() {
        var $select = jQuery(this);
        $metaTable.find("tr").eq($select.val()).show()
            .find("input").eq(0).focus();
        $select.children("option[value='"+ $select.val() + "']").remove();
        if ($select.children("option").length < 2)
            $select.parents("tr").remove();
        else
            $select.val('');
    });
    $metaTable.append($newTag);
}

// ----------------------------------------------------------------------------
// Protection and periodic checking and saving
function protectAndAutoCheck($editing) {
    // Protect
    jQuery("body").on("click", "a", function(event) {
        var message = "Do you really want to quit the editor?";
        var lang = navigator.language || navigator.userLanguage;
        lang = lang.split("-")[0];
        if (!confirm(i18n[lang] && i18n[lang][message] || message)) {
            event.preventDefault();
        }
    });

    // Read checking values
    var $form = jQuery("form");
    if (!$form.length || !$editing.length) return;
    var check = $editing.data("autocheck");
    if (!check) return;
    var cycles = parseInt(String(check).split(",")[1] || 0);
    check = parseInt(String(check).split(",")[0] || 0);
    if (!check) return;
    $editing.data("autocycle", cycles);

    // Set auto checking and saving
    setInterval(function() {
        var url, cycle = $editing.data("autocycle") - 1;
        if (cycle <= 0)
            $editing.data("autocycle", cycles);
        else
            $editing.data("autocycle", cycle);
        url = cycles && cycle <= 0 ? "/file/autosave" : "/file/autocheck";
        for (var i = 0; i < codemirrors.length; i++)
            codemirrors[i].save();
        jQuery.ajax({
            dataType: "json",
            url: $form.attr("action").replace(/\/file\/(write|edit)/, url),
            type: $form.attr("method"),
            data: $form.serialize(),
            success: function(data) {
                if (data && data.error)
                    $form.find("#flash.alert").remove().end()
                    .find("#content").prepend(
                        '<div id="flash" class="alert"><div>'
                            + data.error + "</div></div>")
                    .children("#flash.alert").hide().slideDown('slow')
                    .delay(12000).slideUp('slow');
            }
        });
    }, check * 1000);
}
