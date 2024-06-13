/* $(document).ready(function () {
    $('#data').DataTable({
        ajax: '/api/data',
        columns: [
            {data: 'nombre'},
            {data: 'apellido1', searchable: true},
            {data: 'apellido2', orderable: false, searchable: false},
            {data: 'telefono', orderable: false, searchable: false},
            {data: 'direccion'},
            {
                data: null,
                orderable: false,
                searchable: false,
                render: function (data, type, row) {
                    return `
                    <a href="/edit-alumno/${row.alumno_id}" class="btn btn-secondary btn-sm">Editar</a>
                    <a href="/delete-alumno/${row.alumno_id}" class="btn btn-danger btn-sm btn-delete">Borrar</a>
                    `;
                }
            }
        ],
        drawCallback: function () {
            // Agregar evento click a los botones de borrar después de que la tabla se haya renderizado
            const btnDelete = document.querySelectorAll('.btn-delete');
            if (btnDelete) {
                btnDelete.forEach((btn) => {
                    btn.addEventListener('click', function (e) {
                        if (!confirm('Seguro que desea eliminar este registro?')) {
                            e.preventDefault();
                        }
                    });
                });
            }
        }
    });
}); */