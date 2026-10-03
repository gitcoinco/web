const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');

router.post('/signup', authController.signup);
router.get('/verify-email', authController.verifyEmail);
router.post('/login', authController.login);

module.exports = router;
