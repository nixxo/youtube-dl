# coding: utf-8
from __future__ import unicode_literals

import re

from var_dump import var_dump

from .common import InfoExtractor
from ..utils import (
    js_to_json,
)


class RCScdnIE(InfoExtractor):
    _ALL_REPLACE = {
        'media2vam.corriere.it.edgesuite.net':
            'media2vam-corriere-it.akamaized.net',
        'media.youreporter.it.edgesuite.net':
            'media-youreporter-it.akamaized.net',
        'corrierepmd.corriere.it.edgesuite.net':
            'corrierepmd-corriere-it.akamaized.net',
        'media2vam-corriere-it.akamaized.net/fcs.quotidiani/vr/videos/':
            'video.corriere.it/vr360/videos/',
        '.net//': '.net/',
    }
    _MP4_REPLACE = {
        'media2vam.corbologna.corriere.it.edgesuite.net':
            'media2vam-bologna-corriere-it.akamaized.net',
        'media2vam.corfiorentino.corriere.it.edgesuite.net':
            'media2vam-fiorentino-corriere-it.akamaized.net',
        'media2vam.cormezzogiorno.corriere.it.edgesuite.net':
            'media2vam-mezzogiorno-corriere-it.akamaized.net',
        'media2vam.corveneto.corriere.it.edgesuite.net':
            'media2vam-veneto-corriere-it.akamaized.net',
        'media2.oggi.it.edgesuite.net':
            'media2-oggi-it.akamaized.net',
        'media2.quimamme.it.edgesuite.net':
            'media2-quimamme-it.akamaized.net',
        'media2.amica.it.edgesuite.net':
            'media2-amica-it.akamaized.net',
        'media2.living.corriere.it.edgesuite.net':
            'media2-living-corriere-it.akamaized.net',
        'media2.style.corriere.it.edgesuite.net':
            'media2-style-corriere-it.akamaized.net',
        'media2.iodonna.it.edgesuite.net':
            'media2-iodonna-it.akamaized.net',
        'media2.leitv.it.edgesuite.net':
            'media2-leitv-it.akamaized.net',
    }
    _MIGRATION_MAP = {
        'videoamica-vh.akamaihd': 'amica',
        'media2-amica-it.akamaized': 'amica',
        'corrierevam-vh.akamaihd': 'corriere',
        'media2vam-corriere-it.akamaized': 'corriere',
        'cormezzogiorno-vh.akamaihd': 'corrieredelmezzogiorno',
        'media2vam-mezzogiorno-corriere-it.akamaized': 'corrieredelmezzogiorno',
        'corveneto-vh.akamaihd': 'corrieredelveneto',
        'media2vam-veneto-corriere-it.akamaized': 'corrieredelveneto',
        'corbologna-vh.akamaihd': 'corrieredibologna',
        'media2vam-bologna-corriere-it.akamaized': 'corrieredibologna',
        'corfiorentino-vh.akamaihd': 'corrierefiorentino',
        'media2vam-fiorentino-corriere-it.akamaized': 'corrierefiorentino',
        'corinnovazione-vh.akamaihd': 'corriereinnovazione',
        'media2-gazzanet-gazzetta-it.akamaized': 'gazzanet',
        'videogazzanet-vh.akamaihd': 'gazzanet',
        'videogazzaworld-vh.akamaihd': 'gazzaworld',
        'gazzettavam-vh.akamaihd': 'gazzetta',
        'media2vam-gazzetta-it.akamaized': 'gazzetta',
        'videoiodonna-vh.akamaihd': 'iodonna',
        'media2-leitv-it.akamaized': 'leitv',
        'videoleitv-vh.akamaihd': 'leitv',
        'videoliving-vh.akamaihd': 'living',
        'media2-living-corriere-it.akamaized': 'living',
        'media2-oggi-it.akamaized': 'oggi',
        'videooggi-vh.akamaihd': 'oggi',
        'media2-quimamme-it.akamaized': 'quimamme',
        'quimamme-vh.akamaihd': 'quimamme',
        'videorunning-vh.akamaihd': 'running',
        'media2-style-corriere-it.akamaized': 'style',
        'style-vh.akamaihd': 'style',
        'videostyle-vh.akamaihd': 'style',
        'media2-stylepiccoli-it.akamaized': 'stylepiccoli',
        'stylepiccoli-vh.akamaihd': 'stylepiccoli',
        'doveviaggi-vh.akamaihd': 'viaggi',
        'media2-doveviaggi-it.akamaized': 'viaggi',
        'media2-vivimilano-corriere-it.akamaized': 'vivimilano',
        'vivimilano-vh.akamaihd': 'vivimilano',
        'media2-youreporter-it.akamaized': 'youreporter'
    }
    _MIGRATION_MEDIA = {
        'advrcs-vh.akamaihd': '',
        'corriere-f.akamaihd': '',
        'corrierepmd-corriere-it.akamaized': '',
        'corrprotetto-vh.akamaihd': '',
        'gazzetta-f.akamaihd': '',
        'gazzettapmd-gazzetta-it.akamaized': '',
        'gazzprotetto-vh.akamaihd': '',
        'periodici-f.akamaihd': '',
        'periodicisecure-vh.akamaihd': '',
        'videocoracademy-vh.akamaihd': ''
    }

    def _get_video_src(self, video):
        mediaFiles = video['mediaProfile']['mediaFile']
        src = {}
        # audio
        if video['mediaType'] == 'AUDIO':
            for aud in mediaFiles:
                # todo: check
                src['mp3'] = aud['value']
        # video
        else:
            for vid in mediaFiles:
                if vid['mimeType'] == 'application/vnd.apple.mpegurl':
                    src['m3u8'] = vid['value']
                if vid['mimeType'] == 'video/mp4':
                    src['mp4'] = vid['value']

        # replace host
        for t in src:
            for s, r in self._ALL_REPLACE.items():
                src[t] = src[t].replace(s, r)
            for s, r in self._MP4_REPLACE.items():
                src[t] = src[t].replace(s, r)

        # switch cdn
        if 'mp4' in src and 'm3u8' in src:
            if '-lh.akamaihd' not in src['m3u8'] and 'akamai' in src['mp4']:
                if 'm3u8' in src:
                    matches = re.search(r'(?:https*:)?\/\/(?P<host>.*)\.net\/i(?P<path>.*)$', src['m3u8'])
                    src['m3u8'] = 'https://vod.rcsobjects.it/hls/%s%s' % (
                        self._MIGRATION_MAP[matches.group('host')],
                        matches.group('path').replace(
                            '///', '/').replace(
                            '//', '/').replace(
                            '.csmil', '.urlset'
                        )
                    )
                if 'mp4' in src:
                    matches = re.search(r'(?:https*:)?\/\/(?P<host>.*)\.net\/i(?P<path>.*)$', src['mp4'])
                    if matches:
                        if matches.group('host') in self._MIGRATION_MEDIA:
                            vh_stream = 'https://media2.corriereobjects.it'
                            if src['mp4'].find('fcs.quotidiani_!'):
                                vh_stream = 'https://media2-it.corriereobjects.it'
                            src['mp4'] = '%s%s' % (
                                vh_stream,
                                matches.group('path').replace(
                                    '///', '/').replace(
                                    '//', '/').replace(
                                    '/fcs.quotidiani/mediacenter', '').replace(
                                    '/fcs.quotidiani_!/mediacenter', '').replace(
                                    'corriere/content/mediacenter/', '').replace(
                                    'gazzetta/content/mediacenter/', '')
                            )
                        else:
                            src['mp4'] = 'https://vod.rcsobjects.it/%s%s' % (
                                self._MIGRATION_MAP[matches.group('host')],
                                matches.group('path').replace('///', '/').replace('//', '/')
                            )

        if 'mp3' in src:
            src['mp3'] = src['mp3'].replace(
                'media2vam-corriere-it.akamaized.net',
                'vod.rcsobjects.it/corriere')
        if 'mp4' in src:
            if src['mp4'].find('fcs.quotidiani_!'):
                src['mp4'] = src['mp4'].replace('vod.rcsobjects', 'vod-it.rcsobjects')
        if 'm3u8' in src:
            if src['m3u8'].find('fcs.quotidiani_!'):
                src['m3u8'] = src['m3u8'].replace('vod.rcsobjects', 'vod-it.rcsobjects')

        if 'geoblocking' in video['mediaProfile']:
            if 'm3u8' in src:
                src['m3u8'] = src['m3u8'].replace('vod.rcsobjects', 'vod-it.rcsobjects')
            if 'mp4' in src:
                src['mp4'] = src['mp4'].replace('vod.rcsobjects', 'vod-it.rcsobjects')
        if 'm3u8' in src:
            if src['m3u8'].find('csmil') and src['m3u8'].find('vod'):
                src['m3u8'] = src['m3u8'].replace('.csmil', '.urlset')

        return src

    def _create_formats(self, urls, video_id):
        formats = []

        formats = self._extract_m3u8_formats(
            urls['m3u8'], video_id, 'mp4', entry_protocol='m3u8_native',
            m3u8_id='hls', fatal=False)

        if not formats:
            formats.append({
                'format_id': 'http-mp4',
                'url': urls['mp4']
            })

        self._sort_formats(formats)

        return formats

    def _real_extract(self, url):
        video_id = self._match_id(url)
        mobj = re.search(self._VALID_URL, url).groupdict()

        # if no cdn found look for some iframes
        if not mobj['cdn']:
            classes = [RCSIE, GazzettaIE, CorriereIE]
            webpage = self._download_webpage(url, video_id)
            for c in classes:
                url = c._extract_url(webpage)
                if url:
                    return self.url_result(url, ie=c.ie_key())

        nurl = 'https://video.%s/video-embed/%s' % (mobj['cdn'], video_id)
        page = self._download_webpage(nurl, video_id)
        video_data = self._parse_json(self._search_regex(
            r'[\s;]video\s*=\s*({[\s\S]+?})(?:;|,playlist=)', page, video_id),
            video_id, transform_source=js_to_json)
        formats = self._create_formats(
            self._get_video_src(video_data), video_id)

        return {
            'id': video_id,
            'title': video_data['title'],
            'description': video_data['description'],
            'uploader': video_data['provider'] if video_data['provider'] else mobj['cdn'],
            'formats': formats
        }


class RCSIE(RCScdnIE):
    IE_NAME = 'rcs:rcs'
    _VALID_URL = r'''(?x)
                    https?://
                    (?:
                        video\.(?P<cdn>rcs\.it)|
                        (?:www\.)?
                            (?P<ie>
                                iodonna|
                                amica|
                                stylepiccoli|
                                style\.corriere|
                                living.corriere|
                                oggi|
                                corsedimoto
                            )\.(?:it|com)
                        )/video[\w\W]*?(?:/|\?)(?P<id>[^/=&]+(?=\?|/$|$))'''
    _TESTS = {
        'url': 'https://video.rcs.it/video-embed/iodonna-0001585037',
        'md5': '623ecc8ffe7299b2d0c1046d8331a9df',
        'info_dict': {
            'id': 'iodonna-0001585037',
            'ext': 'mp4',
            'title': 'Sky Arte racconta Madonna nella serie "Artist to icon"',
            'description': 'md5:d41d8cd98f00b204e9800998ecf8427e',
            'uploader': 'rcs.it',
        }
    }, {
        'url': 'https://www.iodonna.it/video-iodonna/personaggi-video/sky-arte-racconta-madonna-nella-serie-artist-to-icon/',
        'md5': '623ecc8ffe7299b2d0c1046d8331a9df',
        'info_dict': {
            'id': 'iodonna-0001585037',
            'ext': 'mp4',
            'title': 'Sky Arte racconta Madonna nella serie "Artist to icon" - Video iO Donna',
            'description': 'md5:d41d8cd98f00b204e9800998ecf8427e',
            'uploader': 'rcs.it',
        }
    }, {
        'url': 'https://www.amica.it/video-post/oscar-2020-renee-zellweger-judy/',
        'md5': '82d09e690b8fffa147f4b7bcf2ffb42c',
        'info_dict': {
            'id': 'amica-0000920309',
            'ext': 'mp4',
            'title': 'Oscar 2020 miglior attrice: Renée Zellweger racconta Judy in esclusiva | Video Amica',
            'description': 'md5:d41d8cd98f00b204e9800998ecf8427e',
            'uploader': 'rcs.it',
        }
    }, {
        'url': 'https://www.corsedimoto.com/video/videotv/video-portimao-new-circuit-motogp-here-riders-fly/',
        'md5': '82de087a67be8dfe586e27cd7694c2e6',
        'info_dict': {
            'id': 'gazzanet-mo05-0000268701',
            'ext': 'mp4',
            'title': 'MotoGP, Portimao la novità: qui i piloti prendono il volo (VIDEO)',
            'uploader': 'rcd',
        }
    }

    @staticmethod
    def _extract_url(webpage):
        entries = [
            mobj.group('url')
            for mobj in re.finditer(r'''(?x)
            (?:
                data-frame-src=|
                <iframe[^\n]+src=
            )
            (["\'])
                (?P<url>(?:https?:)//video\.rcs\.it/video-embed/.+?)
            \1''', webpage)]
        return entries[0] if entries else None


class CorriereIE(RCScdnIE):
    IE_NAME = 'rcs:corriere'
    _VALID_URL = r'''(?x)https?://video\.
                    (?:
                        corrieredelmezzogiorno\.|
                        corrieredelveneto\.|
                        corrieredibologna\.|
                        corrierefiorentino\.
                    )?
                    (?P<cdn>corriere\.it)/(?:.+?)/(?P<id>[^/]+?)(?:$|\?)'''
    _TESTS = {
        'url': 'https://video.corriere.it/sport/formula-1/vettel-guida-ferrari-sf90-mugello-suo-fianco-c-elecrerc-bendato-video-esilarante/b727632a-f9d0-11ea-91b0-38d50a849abb',
        'md5': '0f4ededc202b0f00b6e509d831e2dcda',
        'info_dict': {
            'id': 'b727632a-f9d0-11ea-91b0-38d50a849abb',
            'ext': 'mp4',
            'title': 'Vettel guida la Ferrari SF90 al Mugello e al suo fianco c\'è Leclerc (bendato): il video è esilarante',
            'description': 'md5:93b51c9161ac8a64fb2f997b054d0152',
            'uploader': 'Corriere Tv',
        }
    }, {
        'url': 'https://video.corriere.it/video-embed/b727632a-f9d0-11ea-91b0-38d50a849abb?player',
        'match_only': True
    }, {
        'url': 'https://video.corriere.it/video-360/metro-copenaghen-tutta-italiana/a248a7f0-e2db-11e9-9830-af2de6b1f945',
        'match_only': True
    }

    @staticmethod
    def _extract_url(webpage):
        entries = [
            mobj.group('url')
            for mobj in re.finditer(r'''(?x)
            (?:
                data-frame-src=|
                <iframe[^\n]+src=
            )
            (["\'])
                (?P<url>(?:https?:)//video\.(corriere.+\.)?corriere\.it/video-embed/.+?)
            \1''', webpage)]
        return entries[0] if entries else None


class GazzettaIE(RCScdnIE):
    IE_NAME = 'rcs:gazzetta'
    _VALID_URL = r'https?://video\.(?P<cdn>(?:gazzanet\.)?gazzetta\.it)/(?:.+?)/(?P<id>[^/]+?)(?:$|\?)'
    _TESTS = {
        'url': 'https://video.gazzetta.it/video-motogp-catalogna-cadute-dovizioso-vale-rossi/49612410-00ca-11eb-bcd8-30d4253e0140?vclk=Videobar',
        'md5': 'eedc1b5defd18e67383afef51ff7bdf9',
        'info_dict': {
            'id': '49612410-00ca-11eb-bcd8-30d4253e0140',
            'ext': 'mp4',
            'title': 'Dovizioso, il contatto con Zarco e la caduta. E anche Vale finisce a terra',
            'description': 'md5:8c6e905dc3b9413218beca11ebd69778',
            'uploader': 'AMorici',
        }
    }, {
        'url': 'https://video.gazzetta.it/video-embed/49612410-00ca-11eb-bcd8-30d4253e0140',
        'match_only': True
    }, {
        'url': 'https://video.gazzanet.gazzetta.it/video-embed/gazzanet-mo05-0000260789',
        'match_only': True
    }

    @staticmethod
    def _extract_url(webpage):
        entries = [
            mobj.group('url')
            for mobj in re.finditer(r'''(?x)
            (?:
                data-frame-src=|
                <iframe[^\n]+src=
            )
            (["\'])
                (?P<url>(?:https?:)//video\.(?:gazzanet\.)?gazzetta\.it/video-embed/.+?)
            \1''', webpage)]
        return entries[0] if entries else None

# TODO: youreporter, leitv
