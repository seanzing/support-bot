/**
 * ZING Support Chat Widget
 *
 * Embeddable floating chat bubble for any website.
 *
 * USAGE:
 * Add this script to any website to add ZING support chat:
 *
 *   <script src="https://zing-customer-support-agent.vercel.app/widget.js" async></script>
 *
 * Or with custom configuration:
 *
 *   <script>
 *     window.ZING_WIDGET_CONFIG = {
 *       position: 'bottom-right',  // 'bottom-right' or 'bottom-left'
 *       buttonColor: '#6366F1',    // ZING Indigo (default)
 *       buttonBottom: 50,          // Distance from bottom in px (default: 50)
 *       buttonRight: 35,           // Distance from right edge in px (default: 35)
 *       greeting: 'Need help?',    // Tooltip text
 *       disclaimer: true,          // Show AI disclaimer (default: false)
 *       disclaimerText: 'Custom',  // Custom disclaimer text (optional)
 *       autoOpen: true,            // Auto-open after delay (default: true)
 *       autoOpenDelay: 5000        // Delay before auto-open in ms (default: 5000)
 *     };
 *   </script>
 *   <script src="https://zing-customer-support-agent.vercel.app/widget.js" async></script>
 */
(function() {
  'use strict';

  // Prevent double initialization
  if (window.ZING_WIDGET_LOADED) return;
  window.ZING_WIDGET_LOADED = true;

  // ==========================================================================
  // Configuration
  // ==========================================================================

  // Get the script's src to determine the widget URL
  // Use document.currentScript (modern) with fallback for async loading
  var currentScript = document.currentScript;
  if (!currentScript) {
    // Fallback: find script by src pattern (works with async/defer)
    var scripts = document.getElementsByTagName('script');
    for (var i = 0; i < scripts.length; i++) {
      if (scripts[i].src && scripts[i].src.indexOf('widget.js') !== -1) {
        currentScript = scripts[i];
        break;
      }
    }
  }
  var scriptSrc = (currentScript && currentScript.src) || '';
  var baseUrl = scriptSrc.replace('/widget.js', '') || 'https://support.zing-work.com';

  // Merge user config with defaults - ZING Brand Colors
  var config = Object.assign({
    widgetUrl: baseUrl,
    position: 'bottom-right',
    buttonColor: '#6366F1',           // ZING Indigo primary
    buttonSize: 60,
    buttonBottom: 50,                 // Distance from bottom (px)
    buttonRight: 35,                  // Distance from right edge (px)
    chatWidth: 400,
    chatHeight: 600,
    greeting: 'Chat with ZING Support',
    zIndex: 999999,
    disclaimer: false,                // Show AI disclaimer (default: hidden)
    disclaimerText: '',               // Custom disclaimer text (uses default if empty)
    autoOpen: false,                  // Auto-open chat after delay (default: false)
    autoOpenDelay: 5000               // Delay before auto-open in ms (default: 5000)
  }, window.ZING_WIDGET_CONFIG || {});

  // ==========================================================================
  // Color Utilities
  // ==========================================================================

  function adjustBrightness(hex, percent) {
    var cleanHex = hex.replace('#', '');
    var r = parseInt(cleanHex.substring(0, 2), 16);
    var g = parseInt(cleanHex.substring(2, 4), 16);
    var b = parseInt(cleanHex.substring(4, 6), 16);
    var factor = percent / 100;
    return '#' + Math.round(r * factor).toString(16).padStart(2, '0') +
                 Math.round(g * factor).toString(16).padStart(2, '0') +
                 Math.round(b * factor).toString(16).padStart(2, '0');
  }

  function relativeLuminance(r, g, b) {
    var rs = r / 255, gs = g / 255, bs = b / 255;
    var rL = rs <= 0.03928 ? rs / 12.92 : Math.pow((rs + 0.055) / 1.055, 2.4);
    var gL = gs <= 0.03928 ? gs / 12.92 : Math.pow((gs + 0.055) / 1.055, 2.4);
    var bL = bs <= 0.03928 ? bs / 12.92 : Math.pow((bs + 0.055) / 1.055, 2.4);
    return 0.2126 * rL + 0.7152 * gL + 0.0722 * bL;
  }

  function getContrastTextColor(hex) {
    var cleanHex = hex.replace('#', '');
    var r = parseInt(cleanHex.substring(0, 2), 16);
    var g = parseInt(cleanHex.substring(2, 4), 16);
    var b = parseInt(cleanHex.substring(4, 6), 16);
    return relativeLuminance(r, g, b) > 0.4 ? '#000000' : '#ffffff';
  }

  var hoverColor = adjustBrightness(config.buttonColor, 85);
  var textColor = getContrastTextColor(config.buttonColor);
  var tooltipTextColor = getContrastTextColor(hoverColor);

  // ==========================================================================
  // Styles
  // ==========================================================================

  var styles = document.createElement('style');
  styles.textContent = '\n' +
    '@keyframes zing-bounce {\n' +
    '  0%, 100% { transform: translateY(0); }\n' +
    '  50% { transform: translateY(-4px); }\n' +
    '}\n' +
    '@keyframes zing-fade-in {\n' +
    '  from { opacity: 0; transform: translateY(20px) scale(0.95); }\n' +
    '  to { opacity: 1; transform: translateY(0) scale(1); }\n' +
    '}\n' +
    '@keyframes zing-fade-out {\n' +
    '  from { opacity: 1; transform: translateY(0) scale(1); }\n' +
    '  to { opacity: 0; transform: translateY(20px) scale(0.95); }\n' +
    '}\n' +
    '@keyframes zing-spin {\n' +
    '  0% { transform: rotate(0deg); }\n' +
    '  100% { transform: rotate(360deg); }\n' +
    '}\n' +
    '#zing-chat-button {\n' +
    '  position: fixed;\n' +
    '  ' + (config.position === 'bottom-left' ? 'left' : 'right') + ': ' + config.buttonRight + 'px;\n' +
    '  bottom: ' + config.buttonBottom + 'px;\n' +
    '  width: ' + config.buttonSize + 'px;\n' +
    '  height: ' + config.buttonSize + 'px;\n' +
    '  background: ' + config.buttonColor + ';\n' +
    '  border-radius: 50%;\n' +
    '  cursor: pointer;\n' +
    '  display: flex;\n' +
    '  align-items: center;\n' +
    '  justify-content: center;\n' +
    '  box-shadow: 0 4px 20px rgba(0,0,0,0.2);\n' +
    '  z-index: ' + config.zIndex + ';\n' +
    '  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);\n' +
    '  border: none;\n' +
    '  outline: none;\n' +
    '}\n' +
    '#zing-chat-button:hover {\n' +
    '  filter: brightness(0.85);\n' +
    '  transform: scale(1.1);\n' +
    '  box-shadow: 0 6px 24px rgba(0,0,0,0.25);\n' +
    '}\n' +
    '#zing-chat-button:active {\n' +
    '  transform: scale(0.95);\n' +
    '}\n' +
    '#zing-chat-button.zing-open {\n' +
    '  transform: rotate(180deg);\n' +
    '}\n' +
    '#zing-chat-button.zing-open:hover {\n' +
    '  transform: rotate(180deg) scale(1.1);\n' +
    '}\n' +
    '#zing-chat-button svg {\n' +
    '  transition: transform 0.3s ease;\n' +
    '}\n' +
    '#zing-chat-container {\n' +
    '  position: fixed;\n' +
    '  ' + (config.position === 'bottom-left' ? 'left' : 'right') + ': ' + config.buttonRight + 'px;\n' +
    '  bottom: ' + (config.buttonBottom + config.buttonSize + 10) + 'px;\n' +
    '  width: ' + config.chatWidth + 'px;\n' +
    '  height: ' + config.chatHeight + 'px;\n' +
    '  border-radius: 16px;\n' +
    '  overflow: hidden;\n' +
    '  box-shadow: 0 12px 48px rgba(0,0,0,0.2);\n' +
    '  z-index: ' + (config.zIndex - 1) + ';\n' +
    '  display: none;\n' +
    '  background: #fff;\n' +
    '}\n' +
    '#zing-chat-container.zing-visible {\n' +
    '  display: block;\n' +
    '  animation: zing-fade-in 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;\n' +
    '}\n' +
    '#zing-chat-container.zing-hidden {\n' +
    '  animation: zing-fade-out 0.2s cubic-bezier(0.4, 0, 0.2, 1) forwards;\n' +
    '}\n' +
    '#zing-chat-iframe {\n' +
    '  width: 100%;\n' +
    '  height: 100%;\n' +
    '  border: none;\n' +
    '}\n' +
    '#zing-chat-loader {\n' +
    '  position: absolute;\n' +
    '  top: 50%;\n' +
    '  left: 50%;\n' +
    '  transform: translate(-50%, -50%);\n' +
    '  display: flex;\n' +
    '  flex-direction: column;\n' +
    '  align-items: center;\n' +
    '  gap: 12px;\n' +
    '}\n' +
    '#zing-chat-loader.zing-loaded {\n' +
    '  display: none;\n' +
    '}\n' +
    '#zing-chat-spinner {\n' +
    '  width: 40px;\n' +
    '  height: 40px;\n' +
    '  border: 3px solid #e5e7eb;\n' +
    '  border-top-color: ' + config.buttonColor + ';\n' +
    '  border-radius: 50%;\n' +
    '  animation: zing-spin 0.8s linear infinite;\n' +
    '}\n' +
    '#zing-chat-loader-text {\n' +
    '  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;\n' +
    '  font-size: 14px;\n' +
    '  color: #6b7280;\n' +
    '}\n' +
    '#zing-chat-tooltip {\n' +
    '  position: fixed;\n' +
    '  ' + (config.position === 'bottom-left' ? 'left' : 'right') + ': ' + (config.buttonRight + config.buttonSize + 10) + 'px;\n' +
    '  bottom: ' + (config.buttonBottom + config.buttonSize / 2 - 12) + 'px;\n' +
    '  background: ' + hoverColor + ';\n' +
    '  color: ' + tooltipTextColor + ';\n' +
    '  padding: 8px 14px;\n' +
    '  border-radius: 8px;\n' +
    '  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;\n' +
    '  font-size: 14px;\n' +
    '  white-space: nowrap;\n' +
    '  z-index: ' + (config.zIndex - 2) + ';\n' +
    '  opacity: 0;\n' +
    '  transform: translateX(' + (config.position === 'bottom-left' ? '-10px' : '10px') + ');\n' +
    '  transition: all 0.2s ease;\n' +
    '  pointer-events: none;\n' +
    '}\n' +
    '#zing-chat-button:hover + #zing-chat-tooltip,\n' +
    '#zing-chat-tooltip.zing-show {\n' +
    '  opacity: 1;\n' +
    '  transform: translateX(0);\n' +
    '}\n' +
    '@media (max-width: 480px) {\n' +
    '  #zing-chat-container {\n' +
    '    position: fixed;\n' +
    '    top: 0;\n' +
    '    left: 0;\n' +
    '    right: 0;\n' +
    '    bottom: 0;\n' +
    '    width: 100vw;\n' +
    '    height: 100vh;\n' +
    '    height: 100dvh;\n' +
    '    border-radius: 0;\n' +
    '    padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left);\n' +
    '  }\n' +
    '  #zing-chat-tooltip {\n' +
    '    display: none;\n' +
    '  }\n' +
    '}\n';
  document.head.appendChild(styles);

  // ==========================================================================
  // Create DOM Elements
  // ==========================================================================

  // Chat icon SVG
  var chatIconSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="' + textColor + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>';

  // Close icon SVG
  var closeIconSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="' + textColor + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';

  // Create button
  var button = document.createElement('button');
  button.id = 'zing-chat-button';
  button.innerHTML = chatIconSvg;
  button.setAttribute('aria-label', 'Open ZING Support Chat');
  button.setAttribute('title', config.greeting);

  // Create tooltip
  var tooltip = document.createElement('div');
  tooltip.id = 'zing-chat-tooltip';
  tooltip.textContent = config.greeting;

  // Create chat container
  var container = document.createElement('div');
  container.id = 'zing-chat-container';

  // Create loading spinner
  var loader = document.createElement('div');
  loader.id = 'zing-chat-loader';
  loader.innerHTML = '<div id="zing-chat-spinner"></div><div id="zing-chat-loader-text">Loading...</div>';
  container.appendChild(loader);

  // Create iframe
  var iframe = document.createElement('iframe');
  iframe.id = 'zing-chat-iframe';
  iframe.title = 'ZING Support Chat';
  iframe.allow = 'microphone; camera';

  // Hide loader when iframe loads
  iframe.onload = function() {
    loader.classList.add('zing-loaded');
  };

  container.appendChild(iframe);

  // ==========================================================================
  // Interaction Logic
  // ==========================================================================

  var isOpen = false;
  var hasLoaded = false;
  var autoOpenTimer = null;
  var DISMISSED_KEY = 'zing-widget-dismissed';

  function toggleChat(markDismissed) {
    isOpen = !isOpen;

    if (isOpen) {
      // Load iframe only on first open (lazy loading)
      if (!hasLoaded) {
        // Show loader while iframe loads
        loader.classList.remove('zing-loaded');
        // Build embed URL with config params
        var embedUrl = config.widgetUrl + '?embed=true';
        if (config.disclaimer) {
          embedUrl += '&disclaimer=true';
        }
        if (config.disclaimerText) {
          embedUrl += '&disclaimerText=' + encodeURIComponent(config.disclaimerText);
        }
        iframe.src = embedUrl;
        hasLoaded = true;
      }

      container.classList.remove('zing-hidden');
      container.classList.add('zing-visible');
      button.classList.add('zing-open');
      button.innerHTML = closeIconSvg;
      button.setAttribute('aria-label', 'Close ZING Support Chat');
    } else {
      // Mark as dismissed if user manually closed (not auto-open being cancelled)
      if (markDismissed) {
        try {
          sessionStorage.setItem(DISMISSED_KEY, 'true');
        } catch (e) {
          // sessionStorage might not be available in some contexts
        }
      }
      // Clear auto-open timer if pending
      if (autoOpenTimer) {
        clearTimeout(autoOpenTimer);
        autoOpenTimer = null;
      }

      container.classList.remove('zing-visible');
      container.classList.add('zing-hidden');
      button.classList.remove('zing-open');
      button.innerHTML = chatIconSvg;
      button.setAttribute('aria-label', 'Open ZING Support Chat');

      // Remove hidden class after animation completes
      setTimeout(function() {
        if (!isOpen) {
          container.classList.remove('zing-hidden');
        }
      }, 200);
    }
  }

  // User click handler - mark as dismissed when closing
  function handleButtonClick() {
    toggleChat(isOpen); // Pass true if currently open (closing)
  }

  button.addEventListener('click', handleButtonClick);

  // Close on Escape key (also marks as dismissed)
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && isOpen) {
      toggleChat(true); // Mark as dismissed
    }
  });

  // ==========================================================================
  // Initialize
  // ==========================================================================

  // Wait for DOM ready
  function init() {
    document.body.appendChild(button);
    document.body.appendChild(tooltip);
    document.body.appendChild(container);

    // Show tooltip briefly on load
    setTimeout(function() {
      tooltip.classList.add('zing-show');
      setTimeout(function() {
        tooltip.classList.remove('zing-show');
      }, 3000);
    }, 2000);

    // Auto-open logic with sessionStorage persistence
    if (config.autoOpen) {
      var wasDismissed = false;
      try {
        wasDismissed = sessionStorage.getItem(DISMISSED_KEY) === 'true';
      } catch (e) {
        // sessionStorage might not be available
      }

      if (!wasDismissed) {
        autoOpenTimer = setTimeout(function() {
          if (!isOpen) {
            toggleChat(false); // Open without marking as dismissed
          }
        }, config.autoOpenDelay);
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // ==========================================================================
  // Public API (optional)
  // ==========================================================================

  window.ZingChat = {
    open: function() {
      if (!isOpen) toggleChat();
    },
    close: function() {
      if (isOpen) toggleChat();
    },
    toggle: toggleChat,
    isOpen: function() {
      return isOpen;
    }
  };

})();
