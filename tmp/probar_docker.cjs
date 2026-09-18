const { chromium } = require('C:/Users/julia/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async () => {
  const browser = await chromium.launch({headless:true, channel:'chrome'});
  try {
    const page = await browser.newPage({viewport:{width:1365,height:1100}});
    const errors=[];
    page.on('pageerror', error=>errors.push(error.message));
    await page.goto('http://127.0.0.1:8080/');
    await page.locator('#rfc').fill('PRUEBA-DOCKER');
    await page.locator('#ingresos_mensuales').fill('30000');
    await page.locator('#gastos_mensuales').fill('10000');
    await page.locator('#score_buro_actual').fill('700');
    await page.getByRole('button',{name:'Evaluar escenario'}).click();
    await page.getByText(/Guardada en el historial/).waitFor();
    await page.locator('tbody tr').filter({hasText:'PRUEBA-DOCKER'}).waitFor();
    await page.getByRole('button',{name:'Evaluar escenario'}).click();
    await page.getByText(/Guardada en el historial/).waitFor();
    await page.reload();
    await page.locator('tbody tr').filter({hasText:'PRUEBA-DOCKER'}).waitFor();
    const count = await page.locator('tbody tr').filter({hasText:'PRUEBA-DOCKER'}).count();
    if(count!==1 || errors.length) throw new Error(JSON.stringify({count,errors}));
    await page.screenshot({path:'tmp/docker-desktop.png',fullPage:true});
    await page.setViewportSize({width:390,height:844});
    await page.screenshot({path:'tmp/docker-mobile.png',fullPage:true});
    console.log('OK: Docker guarda, evita duplicados y conserva historial tras recargar; sin errores JS.');
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exit(1)});
