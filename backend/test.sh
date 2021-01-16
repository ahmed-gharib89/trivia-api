dropdb -U ribo trivia_test
createdb -U ribo trivia_test
psql -U ribo -d trivia_test -f trivia.psql
python test_flaskr.py