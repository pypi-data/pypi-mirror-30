!function(t){function e(a){if(n[a])return n[a].exports;var o=n[a]={exports:{},id:a,loaded:!1};return t[a].call(o.exports,o,o.exports,e),o.loaded=!0,o.exports}var n={};return e.m=t,e.c=n,e.p="/_themes/gouvfr/",e(0)}([function(t,e){(function(t){"use strict";function e(){var t="#json_ld",e=JSON.parse(document.querySelector(t).text);return e&&e["@id"]}function n(t){window._paq=window._paq||[];var e=document.getElementById("dataset-recommendations-container"),n=void 0,a=void 0;t.splice(0,i).forEach(function(t,o){n=document.createElement("div"),n.setAttribute("data-track-content",""),n.setAttribute("data-content-name","dataset recommendations"),n.setAttribute("data-content-piece","reco "+o),n.setAttribute("data-content-target","datasets/"+t[0]),n.classList.add("recommendation"),a=document.createElement("div"),a.setAttribute("data-udata-dataset-id",t[0]),n.appendChild(a),e.appendChild(n)}),window._paq.push(["trackContentImpressionsWithinNode",e])}function a(){var t=document.createElement("script");t.type="application/javascript",t.src="/static/widgets.js",t.id="udata",t.onload=o,document.body.appendChild(t)}function o(){udataScript.loadDatasets();var t=document.getElementById("dataset-recommendations");t.style.display="block"}function c(t){fetch(r+t+".json").then(function(t){if(t.ok)return t.json()}).then(function(e){e=e&&e[t],e&&(n(e),a())}).catch(function(t){console.log("Error while fetching recommendations:",t)})}var r="https://raw.githubusercontent.com/etalab/datasets_reco/master/reco_json/",i=2;t.udataDatasetRecos={load:function(){var t=e();t&&c(t)}}}).call(e,function(){return this}())}]);