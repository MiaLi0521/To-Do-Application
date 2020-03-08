from flask import g, request, current_app, url_for, jsonify
from flask_restx import Resource, fields

from todoism import Item
from todoism.apis.v2 import api, ns
from todoism.apis.v2.decorators import auth_required
from todoism.apis.v2.schemas import item_schema, user_schema, items_schema
from todoism.extensions import db

base_info = api.model(
    "baseInfo",
    {
        "api_version": fields.String(description="api版本"),
        "api_base_url": fields.String(description="api根路路径"),
        "current_user_url": fields.String(description="当前登录用户URL"),
        "authentication_url": fields.String(description="授权URL"),
        "item_url": fields.String(description="任务条目URL"),
        "current_user_items_url": fields.String(description="当前登录用户的任务条目URL"),
        "current_user_active_items_url": fields.String(description="当前登录用户的未完成任务条目URL"),
        "current_user_completed_items_url": fields.String(description="当前登录用户的已完成任务条目URL"),
    }
)


@ns.route('/info')
class IndexAPI(Resource):
    @api.marshal_with(base_info)
    def get(self):
        """返回API的基本信息"""
        return {
            "api_version": "1.0",
            "api_base_url": "http://example.com/api/v1",
            "current_user_url": "http://example.com/api/v1/user",
            "authentication_url": "http://example.com/api/v1/token",
            "item_url": "http://example.com/api/v1/items/{item_id }",
            "current_user_items_url": "http://example.com/api/v1/user/items{?page,per_page}",
            "current_user_active_items_url": "http://example.com/api/v1/user/items/active{?page,per_page}",
            "current_user_completed_items_url": "http://example.com/api/v1/user/items/completed{?page,per_page}",
        }


item_parser = api.parser().add_argument("Authorization", type=str, required=True, help="auth bearer", location="headers").\
    add_argument("body", type=str, required=True, help="{'body': 'item body'}", location="json")
page_parser = api.parser().add_argument("page", type=int, required=False, help="分页查询页数", location="args", default=1).\
    add_argument("Authorization", type=str, required=True, help="auth bearer", location="headers")
auth_parser = api.parser().add_argument("Authorization", type=str, required=True, help="auth bearer", location="headers")


@ns.route('/item/<int:item_id>')
class ItemAPI(Resource):
    decorators = [auth_required]

    @api.doc(parser=auth_parser)
    def get(self, item_id):
        """Get item"""
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            api.abort(403)
        return item_schema(item)

    @api.doc(parser=item_parser)
    def put(self, item_id):
        """Edit item"""
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            api.abort(403)
        item.body = item_parser.get('body')
        db.session.commit()
        return '', 204

    @api.doc(parser=auth_parser)
    def patch(self, item_id):
        """Toggle item"""
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api.abort(403)
        item.done = not item.done
        db.session.commit()
        return '', 204

    @api.doc(parser=auth_parser)
    def delete(self, item_id):
        """Delete item"""
        item = Item.query.get_or_404(item_id)
        if g.current_user != item.author:
            return api.abort(403)
        db.session.delete(item)
        db.session.commit()
        return '', 204


@ns.route('/user')
@api.doc(parser=auth_parser)
class UserAPI(Resource):
    decorators = [auth_required]

    def get(self):
        return user_schema(g.current_user)


@ns.route('/items')
class ItemsAPI(Resource):
    decorators = [auth_required]

    @api.doc(paeser=page_parser)
    def get(self):
        """Get current user's all items."""
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['TODOISM_ITEM_PER_PAGE']
        pagination = Item.query.with_parent(g.current_user).paginate(page, per_page)
        items = pagination.items
        current = url_for('.items', page=page, _external=True)
        prev = None
        if pagination.has_prev:
            prev = url_for('.items', page=page - 1, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('.items', page=page + 1, _external=True)
        return items_schema(items, current, prev, next, pagination)

    @api.doc(parser=item_parser)
    def post(self):
        """Create new item."""
        item = Item(body=item_parser.get('body'), author=g.current_user)
        db.session.add(item)
        db.session.commit()
        response = jsonify(item_schema(item))
        response.status_code = 201
        response.headers['Location'] = url_for('.item', item_id=item.id, _external=True)
        return response


@ns.route('/items/active')
@api.doc(paeser=page_parser)
class ActiveItemsAPI(Resource):
    decorators = [auth_required]

    def get(self):
        """Get current user's active items."""
        page = page_parser.get('page')
        per_page = current_app.config['TODOISM_ITEM_PER_PAGE']
        pagination = Item.query.with_parent(g.current_user).filter_by(done=False).paginate(page, per_page)
        items = pagination.items
        current = url_for('.active_items', page=page, _external=True)
        prev = None
        if pagination.has_prev:
            prev = url_for('.active_items', page=page-1, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('.active_items', page=page+1, _external=True)
        return jsonify(items_schema(items, current, prev, next, pagination))


@ns.route('/items/completed')
class CompletedItemsAPI(Resource):
    decorators = [auth_required]

    @api.doc(paeser=page_parser)
    def get(self):
        """Get current user's completed items"""
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['TODOISM_ITEM_PER_PAGE']
        pagination = Item.query.with_parent(g.current_user).filter_by(done=True).paginate(page, per_page)
        items = pagination.items
        current = url_for('.items', page=page, _external=True)
        prev = None
        if pagination.has_prev:
            prev = url_for('.items', page=page-1, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('.items', page=page+1, _external=True)
        return jsonify(items_schema(items, current, prev, next, pagination))

    @api.doc(parser=auth_parser)
    def delete(self):
        """delete current user's completed items"""
        items = Item.query.with_parent(g.current_user).filter_by(done=True).delete()
        db.session.commit()
        return '', 204