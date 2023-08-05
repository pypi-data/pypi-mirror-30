/**
 * Created by skolomoychenko on 24.08.2016.
 */


function select(el, id, fname) {
    var result = objs.add_or_remove(id.toString(), fname);
    if (result) {
        django.jQuery(el).closest('.laporem_lslide').addClass('checked')
    } else {
        django.jQuery(el).closest('.laporem_lslide').removeClass('checked')
    }
    objs.get_galary()
}


var lsit_galarys=[];

    var objs={
        data:{},
        add_or_remove: function (id, fname) {
            if (fname in this.data){
                var index = this.data[fname].indexOf(id);
                if (index === -1){
                    this.add(id, fname);
                    return true
                }else{
                    this.remove(id, fname);
                    return false;
                }
            }else{
                this.add(id, fname);
                return true;
            }
        },
        add: function (id, fname) {
            if (fname in this.data){
                var index = this.data[fname].indexOf(id);
                if (index === -1) {
                    this.data[fname].push(id);
                }
            }else{
                this.data[fname]=[id];
            }
        },
        remove: function (id, fname) {
            var index = this.data[fname].indexOf(id);
            this.data[fname].splice(index, 1);
        },
        get_galary: function (fname) {
            if (fname in this.data) {
                return this.data[fname]
            }else{
                return []
            }
        }
    };





    function select_all_laporem(el, fname) {
        var slides = django.jQuery('.laporem_lslide', django.jQuery(el).closest('.laporem_field'));
        if (slides.length === objs.get_galary(fname).length){
            slides.each(function () {
                objs.remove(this.getAttribute('data-id'), fname);
                django.jQuery(this).removeClass('checked')
            });
        }else{
            slides.each(function () {
                objs.add(this.getAttribute('data-id'), fname);
                django.jQuery(this).addClass('checked')
            });
        }
    }

    function delete_laporem_select(classname, fname) {
        var ids = objs.get_galary(fname);
        if (ids.length > 0) {
            if (confirm("Удалить выделенное?")) {
                django.jQuery('.loader').fadeIn();
                django.jQuery.ajax({
                    type: "POST",
                    url: "/laporem/delete_select/",
                    data: {ids: ids, 'classname': classname},
                    success: function (data) {
                        django.jQuery('#iG-'+fname+' .laporem_lslide.checked').remove();
                        for (var i = 0; i < ids.length; i++) {
                          objs.remove(ids[i], fname);
                        }
                        django.jQuery('.loader').fadeOut();
                    },
                    error: function (xhr, str) {
                        alert('Возникла ошибка: ' + xhr.responseCode);
                    }
                })
            }
        }
    }


    function delete_laporem_obj(classname, id, el) {
        if (confirm("Удалить?")) {
            django.jQuery('.loader').fadeIn();
            django.jQuery.ajax({
                type: "GET",
                url: "/laporem/" + classname + "/" + id + "/delete",
                success: function (data) {
                    django.jQuery(el).closest('.laporem_lslide').remove();
                    django.jQuery(window).resize();
                    django.jQuery('.loader').fadeOut();
                },
                error: function (xhr, str) {
                    alert('Возникла ошибка: ' + xhr.responseCode);
                }
            })
        }
    }





    function loadfiles(element ,files){
            var form = new FormData(django.jQuery('form').get(0));
            django.jQuery('.loader').fadeIn();
            if (files){
                var name = django.jQuery('.file', django.jQuery(element).closest('.laporem_field')).attr('name');
                for (var i in files) {
                    form.append(name, files[i]);
                }
            }
            var add_file = django.jQuery('.add_file', django.jQuery(element).closest('.laporem_field'));
            var laporem_progress = django.jQuery('.laporem_progress-bar', django.jQuery(element).closest('.laporem_field'));
            var curent_persent = django.jQuery('.laporem_progress-bar .curent_persent', django.jQuery(element).closest('.laporem_field'));
            add_file.hide();
            laporem_progress.show();
            django.jQuery.ajax({
                type: "POST",
                url: "/laporem/loadfiles/",
                cache: false,
                processData: false,
                contentType: false,
                data: form,
                success: function(data) {
                    var gal = django.jQuery('.IG', django.jQuery(element).closest('.laporem_field'));
                    gal.append(data);
                    var field = gal.data('field');
                    add_file.show();
                    laporem_progress.hide();
                },
                error:  function(xhr, str){
                    alert('Возникла ошибка: ' + xhr.responseCode);
                },
                xhr: function () {
                    var xhr = new window.XMLHttpRequest();
                    xhr.upload.addEventListener('progress', function (e){
                        if(e.lengthComputable){
                            var max = e.total;
                            var current = e.loaded;
                            var Percentage = (current * 100)/max;
                            curent_persent.css({'width': Percentage +"%"});
                        }
                    }, false);
                    return xhr;
                }
            });

    }

    function move_laporem(element) {
        var gal = django.jQuery(element).closest('.IG');
        var list = [];
        django.jQuery('.laporem_lslide', gal).each(function () {
            list.push(django.jQuery(this).data('id'))
        });
        django.jQuery.get("/laporem/move/", {
            list: list,
            laporem_model_file: gal.data('laporem-model-file')
        },function () {
            django.jQuery('.loader', element).hide();
        })
    }

(function($){
    $(document).ready(function () {
        $('.file').change(function () {
            loadfiles(this);
        });

        function handleFileSelect(evt) {
            evt.stopPropagation();
            evt.preventDefault();
            var files = evt.dataTransfer.files;
            loadfiles(this, files);
        }

        function handleDragOver(evt) {
            evt.stopPropagation();
            evt.preventDefault();
            $(this).addClass('dragover')
        }

        function handleDragLeave(evt) {
            evt.stopPropagation();
            evt.preventDefault();
            $(this).removeClass('dragover')
        }



        $('.dragzone').each(function (dropZone) {
            this.addEventListener('dragover', handleDragOver, false);
            this.addEventListener('drop', handleFileSelect, false);
            this.addEventListener('dragleave', handleDragLeave, false);
            this.addEventListener('drop', handleDragLeave, false);
        })

        $('.IG').sortable({
            cursor: '-webkit-grabbing',
            opacity: 0.5,
            distance: 20,
            placeholder: 'emptySpace',
            remove: function (event, ui) {
                $(ui.item).toggleClass('lets_moved')
            },
            update: function (event, ui) {
                move_laporem(ui.item)
            }
        });

    })
})(django.jQuery);

