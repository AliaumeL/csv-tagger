# CSV tagger

This is a demo project for CSV tagging, that serves as support
for the series of posts on [ui and ux for small programs][]
started on [Aliaume's personal webpage][].

[ui and ux for small programs]: https://irif.fr/~alopez/posts/2023-09-20-ui-ux-small-programs-1.html
[Aliaume's personal webpage]: https://irif.fr/~alopez/

## Project Description

Given a CSV file with columns containing `date`, `strings`, and `floats`
the goal is to add a new column (or edit an existing column)
whose content is a `string` belonging to a finite set.
Typically, the input CSV will be a list of bank transactions,
and the goal is to assign a category to every transaction. The archetypical 
example of category being `solo` or `shared` expanse.


### Why?

The above program is almost one hundred percent about human interface.
Indeed, the categories `solo` or `shared` cannot be inferred from
the input data, and every tag *has to be asked to the user*. Therefore,
the algorithmic content of the program is reduced to its bare minimum:
parsing CSV files, writing CSV files, and managing a list of records.
This allows us to focus on the human interface, and compare approaches
in different languages, without having to fundamentally change
the underlying data model.


### How?

The repository is organised in terms of sub-folders, one sub-folder
corresponds to one way to solve the project's requirements.
The different implementations do not need to be code, and their
development stage may differ. Every sub-folder contains a `README.md`
file explaining the approach and listing its pros and cons.

### Evaluation?

The evaluation, comparison, and list of the approaches
remains a work in progress. In an ideal world, you will find
below a list of key indicators that discriminates the maturity of the approaches
(non-linear edition, state restoration, etc.), together with
informal indicators of their usability (easy to install, easy to use,
easy to modify, etc.).
