INSERT OR IGNORE INTO scenarios VALUES (1, 'Five-sector sample');

INSERT OR IGNORE INTO sectors VALUES
    (1, 0, 'Agriculture'), (1, 1, 'Manufacturing'), (1, 2, 'Energy'),
    (1, 3, 'Transport'), (1, 4, 'Services');

INSERT OR IGNORE INTO demands VALUES
    (1, 0, 66), (1, 1, 48), (1, 2, 30), (1, 3, 25), (1, 4, 40);

INSERT OR IGNORE INTO consumption_matrix VALUES
    (1, 0, 0, .20), (1, 0, 1, .10), (1, 0, 2, .05), (1, 0, 3, .02), (1, 0, 4, .03),
    (1, 1, 0, .10), (1, 1, 1, .20), (1, 1, 2, .10), (1, 1, 3, .08), (1, 1, 4, .04),
    (1, 2, 0, .10), (1, 2, 1, .15), (1, 2, 2, .20), (1, 2, 3, .12), (1, 2, 4, .09),
    (1, 3, 0, .06), (1, 3, 1, .08), (1, 3, 2, .05), (1, 3, 3, .15), (1, 3, 4, .04),
    (1, 4, 0, .05), (1, 4, 1, .10), (1, 4, 2, .06), (1, 4, 3, .08), (1, 4, 4, .20);
