jQuery(function($){
    var $modal = $('#editor-modal'),
        $editor = $('#editor'),
        $editorTitle = $('#editor-title'),
        ft = FooTable.init('#showcase-example-1', {
            columns: $.get("../../content/columns.json"),
            rows: $.get("../../content/rows.json"),
            editing: {
                addRow: function(){
                    $modal.removeData('row');
                    $editor[0].reset();
                    $editorTitle.text('Add a new row');
                    $modal.modal('show');

                    // Ajout d'un événement de soumission au formulaire d'édition
                    $editor.off('submit').on('submit', function(e) {
                        if (this.checkValidity && !this.checkValidity()) return;
                        e.preventDefault();

                        var values = {
                            firstName: $editor.find('#firstName').val(),
                            lastName: $editor.find('#lastName').val(),
                            jobTitle: $editor.find('#jobTitle').val(),
                            startedOn: $editor.find('#startedOn').val(),
                            dob: $editor.find('#dob').val(),
                            status: $editor.find('#status option:selected').val()
                        };

                        // Utiliser la fonction AJAX pour ajouter la ligne
                        addRowAjax(values);
                    });
                },
                editRow: function(row){
                    var values = row.val();
                    $editor.find('#firstName').val(values.firstName);
                    $editor.find('#lastName').val(values.lastName);
                    $editor.find('#jobTitle').val(values.jobTitle);
                    $editor.find('#status').val(values.status);
                    $editor.find('#startedOn').val(values.started.format('YYYY-MM-DD'));
                    $editor.find('#dob').val(values.dob.format('YYYY-MM-DD'));
                    $modal.data('row', row);
                    $editorTitle.text('Edit row #' + values.id);
                    $modal.modal('show');

                    // Ajout d'un événement de soumission au formulaire d'édition
                    $editor.off('submit').on('submit', function(e) {
                        if (this.checkValidity && !this.checkValidity()) return;
                        e.preventDefault();

                        var editedValues = {
                            firstName: $editor.find('#firstName').val(),
                            lastName: $editor.find('#lastName').val(),
                            jobTitle: $editor.find('#jobTitle').val(),
                            startedOn: $editor.find('#startedOn').val(),
                            dob: $editor.find('#dob').val(),
                            status: $editor.find('#status option:selected').val()
                        };

                        // Utiliser la fonction AJAX pour mettre à jour la ligne
                        editRowAjax(editedValues);
                    });
                },
                deleteRow: function(row){
                    if (confirm('Are you sure you want to delete the row?')){
                        deleteRowAjax(row);
                    }
                }
            }
        });

    function addRowAjax(values) {
        $.ajax({
            url: '/url_pour_ajouter',
            method: 'POST',
            data: values,
            success: function(response) {
                // Réponse de succès, mettre à jour la table ou effectuer d'autres actions
                console.log('Row added successfully:', response);
            },
            error: function(xhr, status, error) {
                // Gérer les erreurs
                console.error('Error adding row:', error);
            }
        });
    }

    function editRowAjax(values) {
        $.ajax({
            url: '/url_pour_modifier',
            method: 'POST',
            data: values,
            success: function(response) {
                // Réponse de succès, mettre à jour la table ou effectuer d'autres actions
                console.log('Row updated successfully:', response);
            },
            error: function(xhr, status, error) {
                // Gérer les erreurs
                console.error('Error updating row:', error);
            }
        });
    }

    function deleteRowAjax(row) {
        $.ajax({
            url: '/url_pour_supprimer',
            method: 'POST',
            data: row.val(),
            success: function(response) {
                // Réponse de succès, mettre à jour la table ou effectuer d'autres actions
                console.log('Row deleted successfully:', response);
            },
            error: function(xhr, status, error) {
                // Gérer les erreurs
                console.error('Error deleting row:', error);
            }
        });
    }
});
