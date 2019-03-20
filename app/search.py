"""
该文件包含搜索引擎的三个功能
1. 搜索（最重要）
2. 添加索引条目（用户添加动态之后，需要添加到全文中）
3. 删除索引条目（如果支持了用户删除动态，则需要删除索引中条目）
"""

from flask import current_app


def add_to_index(index, model):
    """
    添加索引条目
    """
    # 如果当前搜索引擎服务没有建立连接对象，则不予处理
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, doc_type=index, id=model.id,
                                    body=payload)


def remove_from_index(index, model):
    """删除索引条目"""
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, doc_type=index, id=model.id)


def query_index(index, query, page, per_page):
    """查询索引"""
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index, doc_type=index,
        body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
              'from': (page-1)*per_page, 'size': per_page})
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']
