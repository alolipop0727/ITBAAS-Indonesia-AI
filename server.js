'use strict';
const app = require('./src/app.cjs');
const port = Number(process.env.PORT || 3100);
app.listen(port, () => {
  console.log(`padma-itbaas-ai listening on :${port}`);
});
