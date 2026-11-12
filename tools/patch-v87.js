// Χρήση: node patch-v87.js <φάκελος-με-Index.html-και-Κώδικας.js>   (v87: Μασούτης στη θέση του Κρητικού)
const fs = require('fs'), path = require('path');
const dir = process.argv[2];
function rep(file, pairs) {
  const p = path.join(dir, file); let s = fs.readFileSync(p, 'utf8');
  for (const [a, b] of pairs) { if (s.split(a).length !== 2) throw new Error('Δεν βρέθηκε ακριβώς 1 φορά: ' + a); s = s.replace(a, () => b); }
  fs.writeFileSync(p, s);
}
rep('Index.html', [
  ["kritikos: 'Κρητικός', lidl: 'Lidl', halkiadakis: 'Χαλκιαδάκης' };", "masoutis: 'Μασούτης', lidl: 'Lidl', halkiadakis: 'Χαλκιαδάκης' };"],
  ["kritikos: 'Κρητικό', lidl: 'Lidl', halkiadakis: 'Χαλκιαδάκη' };", "masoutis: 'Μασούτη', lidl: 'Lidl', halkiadakis: 'Χαλκιαδάκη' };"],
  ["kritikos: 'στον Κρητικό', lidl:", "masoutis: 'στο Μασούτη', lidl:"],
  ["«φθηνότερο στον Κρητικό»", "«φθηνότερο στο Μασούτη»"],
  ['<a href="https://kritikos-sm.gr/fulladia/fulladio/" target="_blank" rel="noopener">Φυλλάδιο<b>Κρητικός</b></a>',
   '<a href="https://www.masoutis.gr/promotion" target="_blank" rel="noopener">Φυλλάδιο<b>Μασούτης</b></a>'],
  ["function takeShop(r) { r.forEach(o => { if (qWant[o.id] != null) o.qty = qWant[o.id]; }); shop = r; }",
   "function dropKritikos(o) { if (o && (o.chain === 'kritikos' || o.refChain === 'kritikos')) { o.chain = ''; o.ref = ''; o.sel = ''; o.refChain = ''; } return o; }\n" +
   "function takeShop(r) { r.forEach(o => { dropKritikos(o); if (qWant[o.id] != null) o.qty = qWant[o.id]; }); shop = r; }"],
  ["shop = Array.isArray(c) ? c.filter(o => o && typeof o === 'object') : []; } catch (e) {}",
   "shop = Array.isArray(c) ? c.filter(o => o && typeof o === 'object').map(o => { if (o.chain === 'kritikos' || o.refChain === 'kritikos') { o.chain = ''; o.ref = ''; o.sel = ''; o.refChain = ''; } return o; }) : []; } catch (e) {}"],
  ["const APP_VERSION = 86;", "const APP_VERSION = 87;"],
]);
rep('Κώδικας.js', [["const APP_VERSION = 86;", "const APP_VERSION = 87;"]]);
console.log('OK');
