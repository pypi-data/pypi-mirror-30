var gadjo_js = gadjo_js || {};
(function () {
    if (gadjo_js.loaded) return
    gadjo_js.loaded = true;
    var $ = jQuery;
    var popup_script_loaded = {};
    var deferred_timeout = function (duration) {
        var dfd = $.Deferred();
        setTimeout(function () {
            dfd.resolve();
        }, duration);
        return dfd.promise();
    }
    window.displayPopup = function(event)
    {
        /* Opens the target link into a dialog box
         *
         * The target link is extracted from the @href attribute for anchors or
         * from the @data-url attribute for other tags.
         *
         * The dialog title is extracted from "#appbar h2" (this selector can be
         * changed with a @data-title-selector attribute on the anchor tag).
         *
         * The dialog content is extracted from "form" (this selector can be
         * changed with a @data-selector attribute).
         *
         * Buttons (both <button> and <a>) are extracted from the content and
         * converted into proper dialog buttons.  A button with "cancel" as its
         * class will have its action changed to simply close the dialog, without
         * server processing.
         *
         * After loading the dialog content, a gadjo:dialog-loaded event is
         * triggered on the anchor with the dialog content as argument.
         *
         * Alternatively the server may notice the ajax request and answer with
         * an appropriate JSON response. In that case it should have a 'content'
         * attribute with the HTML content, or a 'location' attribute in case of
         * a redirect.
         *
         * In case of such a redirect, a gadjo:dialog-done event is triggered on
         * the anchor and can be cancelled to prevent the default redirect
         * behaviour.
         *
         * The JSON support depends on the presence of the jQuery Form plugin.
         *
         * Submit is done in place if the $anchor has a data-inplace-submit="true"
         * attribute, a gadjo:dialog-done event is triggered on success, a
         * gadjo:dialog-submit-error event is triggered on failure.
         *
         * Dialog is modal by default, set data-modal="false" for non-modal
         * dialogs.
         */
        var $anchor = $(this);
        var url = $anchor.attr('href') || $anchor.data('url');
        var selector = $anchor.data('selector') || 'form:not(.gadjo-popup-ignore)';
        var title_selector = $anchor.data('title-selector') || '#appbar h2';
        var inplace_submit = $anchor.data('inplace-submit');
        var modal = $anchor.data('modal');
        if (url == '#') {
            return false;
        }
        if (modal === undefined) {
            modal = true;
        }

        function show_error(message) {
          /* Add a div to body to show an error message and fade it out after 3
           * seconds */
          $('<div id="gadjo-ajax-error"></div>')
            .text(message)
            .appendTo('body')
            .delay(3000)
            .fadeOut(400, function () {
              $(this).remove();
            });
        }

        function ajaxform_submit(data, status, xhr, form) {
            if ('location' in data) {
                var e = $.Event('gadjo:dialog-done');
                if (document.contains($anchor[0])) {
                    $anchor.trigger(e, data);
                } else {
                    $(document).trigger(e, data);
                }
                /* check if the event action has been prevented, and don't do
                 * anything in that case. */
                if (! e.isDefaultPrevented()) {
                    if (data.location.split('#')[0] == window.location.href.split('#')[0]) {
                        window.location.reload(true);
                    }
                    window.location = data.location;
                }
            } else {
                var $form = $(form);
                $form.empty().append($(data.content).find(selector).children());
                $form.find('.buttons').hide();
                if (document.contains($anchor[0])) {
                  $anchor.trigger('gadjo:dialog-loaded', $form);
                } else {
                  $(document).trigger('gadjo:dialog-loaded', $form);
                }
            }
        }

        /* Close existing dialog boxes */
        $(".ui-dialog-content").dialog("destroy");

        $.ajax({
            url: url,
            success: function(html) {
                var is_json = typeof html != 'string';
                if (is_json) {
                    /* get html out of json */
                    var html = html.content;
                } else {
                    var html = html;
                }
                var $html = $(html);
                /* load additional scripts from popup */
                var $script = $html.filter('script[src]');
                var loading = [];
                for (var i = 0; i < $script.length; i++) {
                    var script = $script[i];
                    var src = script.attributes.src.value;
                    if ($('script[src="' + src + '"]').length) {
                        continue;
                    }
                    if (popup_script_loaded[src]) {
                        continue;
                    }
                    popup_script_loaded[src] = true;
                    loading.push($.ajax({
                        url: src,
                        dataType: 'script',
                        cache: true,
                        success: function () {},
                    }));
                }
                /* add millisecond timeout to let additional scripts load */
                $.when(loading, deferred_timeout(100)).always(function () {
                    /* get content and form (if different) ouf of html */
                    var $content = $html.find(selector);
                    if ($content.is('form')) {
                        var $form = $content;
                    } else {
                        var $form = $content.find('form');
                    }

                    /* get title out of html */
                    var title = $html.find(title_selector).text();

                    $content.dialog({
                      modal: modal,
                      'title': title,
                      width: 'auto',
                      close: function (ev, ui) {
                        $(this).dialog('destroy');
                      },
                    });

                    /* if the form doesn't have an @action attribute, set it to URL */
                    if (! $form.attr('action')) {
                        $form.attr('action', url);
                    }

                    /* hide buttons from content and convert buttons (<button> and <a>)
                     * into proper dialog buttons */
                    $content.find('.buttons').hide();

                    var buttons = Array();
                    $content.find('.buttons button, .buttons a').each(function(idx, elem) {
                        var $elem = $(elem);
                        var button = Object();

                        button.text = $elem.text();
                        if ($elem.prop('disabled')) {
                            button.disabled = 'disabled';
                        }
                        if ($elem.hasClass('cancel')) {
                            /* special behaviour for the cancel button: do not send
                             * anything to server, just close the dialog */
                            button.click = function() { $content.dialog('destroy'); return false; };
                        } else {
                            button.click = function() {
                                if (inplace_submit) {
                                    var action_url = $form.attr('action');
                                    if ($form[0].checkValidity() === false) {
                                        /* if HTML5 validation fails, we trigger a
                                         * click to get the errors displayed */
                                        $form.find('button').click();
                                        return false;
                                    }
                                    $('.ui-dialog-buttonpane button').button('disable');
                                    $.ajax({
                                        type: 'POST',
                                        url: action_url,
                                        data: $form.serialize(),
                                    }).success(function(data) {
                                        $anchor.trigger('gadjo:dialog-done', data);
                                        $content.dialog('destroy');
                                    }).fail(function() { $anchor.trigger('gadjo:dialog-submit-error');
                                    });
                                } else {
                                    $content.find('button').click();
                                }
                                return false;
                            };
                        }

                        /* add custom classes to some buttons */
                        if ($elem.hasClass('submit-button')) {
                            button.class = 'submit-button';
                        } else if ($elem.hasClass('cancel') || $elem.hasClass('cancel-button')) {
                            button.class = 'cancel-button';
                        } else if ($elem.hasClass('delete-button')) {
                            button.class = 'delete-button';
                        }
                        buttons.push(button);
                    });

                    buttons.reverse();
                    $content.dialog('option', 'buttons', buttons);

                    /* focus initial input field */
                    if ($form.find('input:visible').length) {
                        $form.find('input:visible')[0].focus();
                    }

                    /* if received content was in json, apply jQuery Form plugin on it */
                    if (is_json && $.fn.ajaxForm != undefined) {
                        $form.ajaxForm({
                          success: ajaxform_submit,
                          error: function (jqXHR, textStatus, errorThrown) {
                            show_error("Dialog box submit failed: " + textStatus + " " + errorThrown);
                          }
                        });
                    }
                    $anchor.trigger('gadjo:dialog-loaded', $content);
                });
                return false;
            },
            error: function (jqXHR, textStatus, errorThrown) {
              show_error("Dialog box loading failed: " + textStatus + " " + errorThrown);
            }
        });
        return false;
    }

    var storage = undefined;
    try {
        window.localStorage._gadgo_test = true;
        window.localStorage.removeItem('_gadjo_test');
        storage = window.localStorage;
    } catch(e) {
        try {
            window.sessionStorage._gadjo_test = true;
            window.sessionStorage.removeItem('_gadjo_test');
            storage = window.sessionStorage;
        } catch(e) {
            storage = Object();
        }
    }

    $(function() {
      var cookie_domain = window.location.hostname.split('.').slice(1).join('.');

      function readCookie(name) { /* http://www.quirksmode.org/js/cookies.html */
        var nameEQ = name + "=";
        var ca = document.cookie.split(';');
        for(var i=0;i < ca.length;i++) {
          var c = ca[i];
          while (c.charAt(0)==' ') c = c.substring(1,c.length);
          if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
        }
        return null;
      }

      function set_sidepage_status(sidepage_status) {
        storage.sidepage_status = sidepage_status;
        if (cookie_domain) {
          var date = new Date();
          date.setTime(date.getTime() + (10 * 86400 * 1000)); /* a long week */
          document.cookie = 'gadjo_sidepage_status=' + sidepage_status +
                            '; expires=' + date.toGMTString() +
                            '; domain=.' + cookie_domain +
                            '; path=/';
        }
      }
      function get_sidepage_status() {
        if (window.location.protocol == 'file:') {
          /* don't open sidepage when loading from a file:// */
          return 'collapsed';
        }
        var sidepage_status = null;
        if (cookie_domain) {
          sidepage_status = readCookie('gadjo_sidepage_status');
        } else {
          sidepage_status = storage.sidepage_status;
        }
        if (!sidepage_status &&
                typeof(GADJO_DEFAULT_SIDEPAGE_STATUS) !== "undefined") {
          return GADJO_DEFAULT_SIDEPAGE_STATUS;
        }
        return sidepage_status;
      }

      $(document).on('click.gadjo', 'a[rel=popup]', displayPopup);
      if ($('#sidepage').length) {
        var sidepage_button = $('#sidepage #applabel');
        sidepage_button.on('click', function() {
          $('body').addClass('enable-transitions');
          $('body').toggleClass('sidepage-expanded');
          if ($('body').hasClass('sidepage-expanded')) {
             set_sidepage_status('expanded');
          } else {
             set_sidepage_status('collasped');
          }
        });
        if ($(window).width() > 760) {
          if (get_sidepage_status() == 'expanded') {
            $('body').toggleClass('sidepage-expanded');
          }
        }
      }
    });
    $(function () { /* foldable elements with memory */
      function gadjo_unfold_saved() {
        $('.gadjo-folded').each(function (idx, elem) {
          if (elem.id && sessionStorage['gadjo-foldable-id-' + elem.id + '-' + window.location.pathname] == "true") {
              $(elem).removeClass('gadjo-folded');
          }
        });
      }
      gadjo_unfold_saved()
      $(document).on('gadjo:content-update', gadjo_unfold_saved);
      $('body').on('click', '.gadjo-foldable-widget', function (event) {
        var $parent = $(event.target).closest('.gadjo-foldable');
        $parent.toggleClass('gadjo-folded');
        if ($parent[0].id) {
            sessionStorage['gadjo-foldable-id-' + $parent[0].id + '-' + window.location.pathname] = ! $parent.is('.gadjo-folded');
        }
      });
    });
    $(function () { /* foldable sections */
      $('.section.foldable > h2, .section.foldable > h3').on('click', function() {
        $(this).parent().toggleClass('folded');
      });
    });
    $(function () {
      if ($('body').data('gadjo')) {
        if ($('#sidepage').length == 1) {
          $('body').attr('data-has-sidepage', 'true');
        }
        if ($('body[data-no-moving-header]').length == 0) {
          /* 440 is header image height (500px) - header height (60px) */
          var timestamp = ((new Date().getTime() / 1000) % 86400 ) / (86400 / 440);
          $('div#header').css('background-position', '0 -' + timestamp + 'px');
        }

        /* add × to close notification messages */
        $('.messages > li').each(function(idx, elem) {
          var elem = $('<a aria-hidden="true" class="close">×</a>');
          $(elem).on('click', function() {
            $(this).parent('li').fadeOut('slow');
          });
          $(this).prepend(elem);
        });
      }
    });
    $(function() {
        $('a.extra-actions-menu-opener').on('click', function() {
            $(this).toggleClass('open');
            $('.extra-actions-menu').toggleClass('open');
        });
    });
})();
