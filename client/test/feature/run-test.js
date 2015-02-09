// var casper = require('casper').create();
'use strict';
var x = require('casper').selectXPath;

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
    test.assertHttpStatus(200, 'It can logged in.');
  });

  casper.then(function() {
    test.assertExists('#update-time');
  });

  casper.then(function() {
    casper.wait(1000, function() {
      casper.log('should appear after 1s', 'info');
      test.assertTextDoesntExist('None', 'None does not exist within the body when logged in.');
    });
  });

  casper.then(function() {
    this.click(x('//*[text()="設定"]'));
    this.waitUntilVisible(x('//*[text()="アクション"]'), function() {
      this.test.pass('Settings dropdown is opened');
      this.click(x('//*[text()="アクション"]'));
      casper.wait(1000, function() {
        test.assertUrlMatch(/ajax_actions/, 'Moved into "actions page"');
      });
    });
  });

  casper.run(function() {
    test.done();
  });
});
