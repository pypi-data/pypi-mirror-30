Common Table Expressions (CTE) for Django
=========================================

Installation
------------

::

    pip install django-cte

Usage
-----

Simple Common Table Expressions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Simple CTE queries can be constructed using ``With``. A custom
``CTEManager`` is used to add the CTE to the final query.

.. code:: py

    from django_cte import CTEManager, With

    class Order(Model):
        objects = CTEManager()
        id = AutoField(primary_key=True)
        region = ForeignKey("Region", on_delete=CASCADE)
        amount = IntegerField(default=0)


    cte = With(
        Order.objects
        .values("region_id")
        .annotate(total=Sum("amount"))
    )

    orders = (
        cte.join(Order, region=cte.col.region_id)
        .with_cte(cte)
        .annotate(region_total=cte.col.total)
        .order_by("amount")
    )

Orders returned by this query will have a ``region_total`` attribute
containing the sum of all order amounts in the order's region.

Recursive Common Table Expressions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Recursive CTE queries can be constructed using ``With.recursive``.

.. code:: py

    class Region(Model):
        objects = CTEManager()
        name = TextField(primary_key=True)
        parent = ForeignKey("self", null=True, on_delete=CASCADE)

    def make_regions_cte(cte):
        return Region.objects.filter(
            # start with root nodes
            parent__isnull=True
        ).values(
            "name",
            path=F("name"),
            depth=Value(0, output_field=IntegerField()),
        ).union(
            # recursive union: get descendants
            cte.join(Region, parent=cte.col.name).values(
                "name",
                path=Concat(
                    cte.col.path, Value("\x01"), F("name"),
                    output_field=TextField(),
                ),
                depth=cte.col.depth + Value(1, output_field=IntegerField()),
            ),
            all=True,
        )

    cte = With.recursive(make_regions_cte)

    regions = (
        cte.join(Region, name=cte.col.name)
        .with_cte(cte)
        .annotate(
            path=cte.col.path,
            depth=cte.col.depth,
        )
        .order_by("path")
    )

Regions returned by this query will have ``path`` and ``depth``
attributes. The results will be ordered by ``path`` (hierarchically by
region name). In this case ``path`` is a ``'\x01'``-delimited string of
region names starting with the root region.

See `tests <./tests>`__ for more advanced examples.

Running tests
-------------

::

    cd django-cte
    mkvirtualenv cte  # or however you choose to setup your environment
    pip install django nose flake8

    nosetests
    flake8 --config=setup.cfg

Uploading to PyPI
-----------------

Optional: install ``pandoc`` for prettier README on PyPI. Use your
preferred package manager to do this. Then install ``pypandoc``.

::

    pip install pypandoc

Finally package and upload the generated files.

::

    pip install twine wheel

    python setup.py sdist bdist_wheel
    twine upload dist/*



