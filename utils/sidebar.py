Traceback:
File "/mount/src/berenbaum-law-app/pages/00_🏠_Dashboard.py", line 13, in <module>
    render_sidebar()
    ~~~~~~~~~~~~~~^^
File "/mount/src/berenbaum-law-app/utils/sidebar.py", line 74, in render_sidebar
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/metrics_util.py", line 531, in wrapped_func
    result = non_optional_func(*args, **kwargs)
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/elements/widgets/button.py", line 1059, in page_link
    return self._page_link(
           ~~~~~~~~~~~~~~~^
        page=page,
        ^^^^^^^^^^
    ...<5 lines>...
        query_params=query_params,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/elements/widgets/button.py", line 1309, in _page_link
    raise StreamlitPageNotFoundError(
    ...<3 lines>...
