import { Bell, CreditCard, Globe, Shield, Mail, Smartphone, Moon, Sun, Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useTheme } from '../../context/ThemeContext';
import { changeUserPassword } from '../../services/userService';

export default function Settings() {
  const { isDarkMode, toggleTheme } = useTheme();
  const [showPassword, setShowPassword] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [settings, setSettings] = useState({
    emailNotifications: true,
    pushNotifications: true,
    smsNotifications: false,
    eventReminders: true,
    marketingEmails: false,
    weeklyDigest: true,
    twoFactorAuth: false,
    language: 'en',
    currency: 'KES'
  });

  const [passwords, setPasswords] = useState({
    current: '',
    new: '',
    confirm: ''
  });

  useEffect(() => {
    // Load saved settings from localStorage
    const savedSettings = localStorage.getItem('user_settings');
    if (savedSettings) {
      try {
        setSettings(JSON.parse(savedSettings));
      } catch (err) {
        console.error('Error loading settings:', err);
      }
    }
  }, []);

  const handleToggle = (key: keyof typeof settings) => {
    const newSettings = { ...settings, [key]: !settings[key] };
    setSettings(newSettings);
    localStorage.setItem('user_settings', JSON.stringify(newSettings));
  };

  const handleChangePassword = async () => {
    setPasswordError('');
    setPasswordSuccess('');

    // Validation
    if (!passwords.current || !passwords.new || !passwords.confirm) {
      setPasswordError('All password fields are required');
      return;
    }

    if (passwords.new !== passwords.confirm) {
      setPasswordError('New passwords do not match');
      return;
    }

    if (passwords.new.length < 8) {
      setPasswordError('New password must be at least 8 characters long');
      return;
    }

    try {
      setIsChangingPassword(true);
      await changeUserPassword(passwords.current, passwords.new);
      setPasswordSuccess('Password changed successfully!');
      // Clear form
      setPasswords({
        current: '',
        new: '',
        confirm: ''
      });
    } catch (err: any) {
      console.error('Error changing password:', err);
      setPasswordError(err.message || 'Failed to change password');
    } finally {
      setIsChangingPassword(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">Settings</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Manage your account preferences</p>
      </div>

      {/* Appearance */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
        <div className="flex items-center gap-3 mb-4">
          {isDarkMode ? <Moon className="w-5 h-5 text-[#27aae2]" /> : <Sun className="w-5 h-5 text-[#27aae2]" />}
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Appearance</h2>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <p className="font-semibold text-gray-900 dark:text-white">Theme</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Choose your preferred theme</p>
          </div>
          <button
            onClick={toggleTheme}
            className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors ${
              isDarkMode ? 'bg-[#27aae2]' : 'bg-gray-300'
            }`}
          >
            <span
              className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                isDarkMode ? 'translate-x-7' : 'translate-x-1'
              }`}
            >
              {isDarkMode ? (
                <Moon className="w-4 h-4 text-[#27aae2] m-1" />
              ) : (
                <Sun className="w-4 h-4 text-gray-400 m-1" />
              )}
            </span>
          </button>
        </div>
      </div>

      {/* Notifications */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
        <div className="flex items-center gap-3 mb-6">
          <Bell className="w-5 h-5 text-[#27aae2]" />
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Notifications</h2>
        </div>
        <div className="space-y-4">
          {[
            { key: 'emailNotifications', icon: Mail, label: 'Email Notifications', desc: 'Receive notifications via email' },
            { key: 'pushNotifications', icon: Bell, label: 'Push Notifications', desc: 'Receive push notifications in browser' },
            { key: 'smsNotifications', icon: Smartphone, label: 'SMS Notifications', desc: 'Receive notifications via SMS' },
            { key: 'eventReminders', icon: Bell, label: 'Event Reminders', desc: 'Get reminded about upcoming events' },
            { key: 'marketingEmails', icon: Mail, label: 'Marketing Emails', desc: 'Receive promotional offers and updates' },
            { key: 'weeklyDigest', icon: Mail, label: 'Weekly Digest', desc: 'Get a summary of events every week' }
          ].map((item) => (
            <div key={item.key} className="flex items-center justify-between py-3 border-b border-gray-100 dark:border-gray-700 last:border-0">
              <div className="flex items-center gap-3">
                <item.icon className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">{item.label}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{item.desc}</p>
                </div>
              </div>
              <button
                onClick={() => handleToggle(item.key as keyof typeof settings)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  settings[item.key as keyof typeof settings] ? 'bg-[#27aae2]' : 'bg-gray-300 dark:bg-gray-600'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    settings[item.key as keyof typeof settings] ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Security */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
        <div className="flex items-center gap-3 mb-6">
          <Shield className="w-5 h-5 text-[#27aae2]" />
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Security</h2>
        </div>
        
        {/* Change Password */}
        <div className="mb-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Change Password</h3>
          
          {/* Error Message */}
          {passwordError && (
            <div className="mb-4 bg-red-50 dark:bg-red-900/20 border-2 border-red-500 rounded-xl p-3 flex items-start space-x-2">
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-700 dark:text-red-400">{passwordError}</p>
            </div>
          )}

          {/* Success Message */}
          {passwordSuccess && (
            <div className="mb-4 bg-green-50 dark:bg-green-900/20 border-2 border-green-500 rounded-xl p-3 flex items-start space-x-2">
              <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-green-700 dark:text-green-400">{passwordSuccess}</p>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Current Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={passwords.current}
                  onChange={(e) => {
                    setPasswords({ ...passwords, current: e.target.value });
                    setPasswordError('');
                    setPasswordSuccess('');
                  }}
                  className="w-full px-4 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-[#27aae2] focus:border-transparent"
                  placeholder="Enter current password"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                New Password
              </label>
              <input
                type={showPassword ? 'text' : 'password'}
                value={passwords.new}
                onChange={(e) => {
                  setPasswords({ ...passwords, new: e.target.value });
                  setPasswordError('');
                  setPasswordSuccess('');
                }}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-[#27aae2] focus:border-transparent"
                placeholder="Enter new password"
                autoComplete="new-password"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Must be at least 8 characters long</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Confirm New Password
              </label>
              <input
                type={showPassword ? 'text' : 'password'}
                value={passwords.confirm}
                onChange={(e) => {
                  setPasswords({ ...passwords, confirm: e.target.value });
                  setPasswordError('');
                  setPasswordSuccess('');
                }}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-[#27aae2] focus:border-transparent"
                placeholder="Confirm new password"
                autoComplete="new-password"
              />
            </div>
            <button
              onClick={handleChangePassword}
              disabled={isChangingPassword || !passwords.current || !passwords.new || !passwords.confirm}
              className={`px-6 py-2 bg-[#27aae2] text-white rounded-lg hover:bg-[#1e8bb8] transition-colors font-semibold disabled:opacity-50 disabled:cursor-not-allowed ${
                isChangingPassword ? 'opacity-70' : ''
              }`}
            >
              {isChangingPassword ? 'Changing Password...' : 'Update Password'}
            </button>
          </div>
        </div>

        {/* Two-Factor Authentication */}
        <div className="pt-6 border-t border-gray-100 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-semibold text-gray-900 dark:text-white">Two-Factor Authentication</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Add an extra layer of security</p>
            </div>
            <button
              onClick={() => handleToggle('twoFactorAuth')}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                settings.twoFactorAuth ? 'bg-[#27aae2]' : 'bg-gray-300 dark:bg-gray-600'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  settings.twoFactorAuth ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
      </div>

      {/* Preferences */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
        <div className="flex items-center gap-3 mb-6">
          <Globe className="w-5 h-5 text-[#27aae2]" />
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Preferences</h2>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Language
            </label>
            <select
              value={settings.language}
              onChange={(e) => {
                const newSettings = { ...settings, language: e.target.value };
                setSettings(newSettings);
                localStorage.setItem('user_settings', JSON.stringify(newSettings));
              }}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-[#27aae2] focus:border-transparent"
            >
              <option value="en">English</option>
              <option value="sw">Swahili</option>
              <option value="fr">French</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Currency
            </label>
            <select
              value={settings.currency}
              onChange={(e) => {
                const newSettings = { ...settings, currency: e.target.value };
                setSettings(newSettings);
                localStorage.setItem('user_settings', JSON.stringify(newSettings));
              }}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-[#27aae2] focus:border-transparent"
            >
              <option value="KES">KES - Kenyan Shilling</option>
              <option value="USD">USD - US Dollar</option>
              <option value="EUR">EUR - Euro</option>
              <option value="GBP">GBP - British Pound</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}
