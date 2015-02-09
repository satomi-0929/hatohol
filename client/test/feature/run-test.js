// var casper = require('casper').create();
'use strict';

casper.test.begin('Login tests', function suite(test) {
  casper.start('http://0.0.0.0:8000/ajax_dashboard', function() {
    test.assertTitle('ダッシュボード - Hatohol', 'Expected top page title');
    test.assertExists('form#loginForm', 'Login form is found');
    this.fill('form#loginForm', {
      inputUserName: 'admin',
      inputPassword: 'hatohol'
    }, false);
  });

  casper.then(function() {
    this.click('input#loginFormSubmit');
    test.assertHttpStatus(200);
    test.assertExists('form#loginForm', 'Login form is found');
  });

  casper.then(function() {
    test.assertExists('#update-time');
  });

  casper.run(function() {
    test.done();
  });
});
