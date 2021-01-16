import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from math import ceil

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


# Helper function tp paginate the questions
def paginate_questions(request, selection, page_num=1):
    # Get the page number or use the default (first page)
    page = request.args.get('page', page_num, type=int)
    # Start question number 
    start = (page - 1) * QUESTIONS_PER_PAGE
    # End question number
    end = start + QUESTIONS_PER_PAGE

    # Geting all questions from the database
    questions = [question.format() for question in selection]
    # Select only 10 questions to view per page
    current_questions = questions[start:end]

    # Return the current questions 
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @Done: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app)

    '''
    @Done: Use the after_request decorator to set Access-Control-Allow
    '''
    # Using after request to allow for access control headers and methods
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                              'GET, PUT, POST, DELETE, OPTIONS')
        # Return the response object after adding the access control
        return response

    '''
    @Done:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories')
    def retrieve_categories():
        '''
        Getting all categories from the database
        as a response for get request using /categories URL
        '''

        # Getting all categories from the database and format it
        categories = Category.query.order_by(Category.id).all()
        cat_dict = {cat.id: cat.type for cat in categories}

        # Check if no categories were found abort with status 404 not found
        if (len(cat_dict) == 0):
            abort(404)

        # return data to view
        return jsonify({
            'success': True,
            'categories': cat_dict,
        })


    '''
    @Done:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route('/questions')
    def retrieve_questions():
        '''
        Getting all questions from the database
        as a response for get request using /questions URL
        including pagination every 10 questions
        '''

        # Get all questions and paginate them 10 questions per page
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        # Getting all categories from the database and format it
        categories = Category.query.order_by(Category.id).all()
        cat_dict = {cat.id: cat.type for cat in categories}
        

        # abort 404 if no questions
        if (len(current_questions) == 0):
            abort(404)

        # return data to view
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'categories': cat_dict,
        })


    '''
    @Done: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        '''
        Delete a question from the database by question_id
        '''
        try:
            # Get the question from the database by question_id
            question = Question.query.filter(Question.id == question_id).one_or_none()

            # Abort if no question retrieved from the database with error status code 404 not found
            if question is None:
                abort(404)

            # Delete the question from the data base
            question.delete()
            # Get all questions from the data base
            selection = Question.query.order_by(Question.id).all()
            # Paginate the current questions to view
            current_questions = paginate_questions(request, selection)

            # Return data to view
            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(selection)
            })

        except:
            # Abort with status code 422 unprocessable
            abort(422)

    '''
    @Done: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions', methods=['POST'])
    def create_search_question():
        '''
        Create a new question or search for questions in the database
        '''
        # Get the body from the request object
        body = request.get_json()
        
        # Get the searchTerm
        search = body.get('searchTerm', None)

        
        # If there is a search term in the body return the questions with matched search term
        if search:
            # Get questions with matched search term
            selection = Question.query.order_by(Question.id).filter(
                Question.question.ilike('%{}%'.format(search)))

            if len(selection.all()) == 0:
                abort(404)

            # Paginate the questions
            current_questions = paginate_questions(request, selection)

            # Return Data to view
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection.all())
            })

        else:
            try:
                # Get the data from the body
                new_question = body.get('question', None)
                new_answer = body.get('answer', None)
                new_category = body.get('category', None)
                new_difficulty = body.get('difficulty', None)

                # Abort if any of the required data for new question is None with status code 422
                if any(item is None for item in [new_question, new_answer, new_category, new_difficulty]):
                    abort(422)

                # Create a new question object and add it to the data base
                question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
                question.insert()

                # Get the questions from the data base
                selection = Question.query.order_by(Question.id).all()
                # Get the last page number to show the created quistion
                page_num = ceil(len(selection) / 10)
                # Paginate the questions and view the last page
                current_questions = paginate_questions(request, selection, page_num=page_num)

                # Return data to view
                return jsonify({
                    'success': True,
                    'created': question.id,
                    'questions': current_questions,
                    'total_questions': len(selection)
                })

            except:
                # Abort with status code 422 unprocessable
                abort(422)

    '''
    @Done: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''

    '''
    @Done: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:category_id>/questions')
    def retrieve_questions_by_selected_category(category_id):
        '''
        Getting all questions for a selected category from the database by category_id
        '''

        # Get the category by category_id or return none if failed
        category = Category.query.filter(Category.id == category_id).one_or_none()

        # Abort with status code 400 for bad request if category wasn't found
        if (category is None):
            abort(400)

        # Get only the question for this category
        selection = Question.query.filter(Question.category == category.id).all()

        # Get current questions to view
        current_questions = paginate_questions(request, selection)

        # return data to view
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'current_category': category.type
        })

    '''
    @Done: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    @app.route('/quizzes', methods=['POST'])
    def create_quiz_questions():
        '''
        Create a new quiz questions based on category if selected
        '''

        # Get the body from the request object
        body = request.get_json()

        # get the previous_questions from the body
        previous_questions = body.get('previous_questions')

        # get the quiz_category from the body
        quiz_category = body.get('quiz_category')

        # abort with status code 400 if quiz_category or previous_questions isn't found
        if ((quiz_category is None) or (previous_questions is None)):
            abort(400)

        # Get the category id
        category_id = quiz_category['id']

        # Get questions for all categories if all was selected 
        if (category_id == 0):
            questions = Question.query
        # or Get question for selected category
        else:
            questions = Question.query.filter(Question.category == quiz_category['id'])

        # if there is previouse_questions filter them from questions
        if len(previous_questions) != 0:
            questions = questions.filter(~Question.id.in_(previous_questions)).all()
        else:
            questions = questions.all()

        if len(questions) == 0:
            return jsonify({
                'success': True
            })

        # Get random question
        question = random.choice(questions)

        # return the question
        return jsonify({
            'success': True,
            'question': question.format()
        })


    '''
    @Done: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': "resource not found"
        }), 404

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': "method not allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': "unprocessable"
        }), 422


    return app
