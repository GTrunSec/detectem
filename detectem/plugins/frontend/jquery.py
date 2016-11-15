from detectem.plugin import Plugin


class JqueryPlugin(Plugin):
    name = 'jquery'
    matchers = [
        {'body': '/\*\! jQuery v(?P<version>[0-9\.]+) \| \(c\)'},
        {'body': '\* jQuery JavaScript Library v(?P<version>[0-9\.]+)'},
        {'url': '/jquery/(?P<version>[0-9\.]+)/jquery(\.min)?\.js'},
        {'url': '/jquery-(?P<version>[0-9\.]+)(\.min)?\.js'},
    ]
