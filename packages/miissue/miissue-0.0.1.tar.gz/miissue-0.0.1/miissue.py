import click
import requests
import json
from StringIO import StringIO

surl  = None
srepo = None
drepo = None
durl  = None
stoken = None
dtoken = None
stat   = "closed"
@click.command()
@click.option('--verbose', is_flag=True, help="verbose mode enabled.")
@click.option('--param', '-p', multiple=True, default='', help='Parameter for Source(s), Destination(d) git urls, repo, stat and tokens?')

def cli(verbose,param):
	"""Git Issue Migration Tool miissue (migration issue = mi~issue) gitbucket to github and vice-versa."""
	if verbose:
	 click.echo("We are in the verbose mode.")
	for p in param:
		global surl, durl, stoken, dtoken, srepo, drepo, stat
		items = format(p).split( )
		if items[0] == 'surl':
			surl = items[1]
		elif items[0] == 'durl':
			durl = items[1]
		elif items[0] == 'stoken':
			stoken = items[1]
		elif items[0] == 'dtoken':
			dtoken = items[1]
		elif items[0] == 'srepo':
			srepo = items[1]
		elif items[0] == 'drepo':
			drepo = items[1]
		elif items[0] == 'stat':
			stat = items[1]

	if surl and srepo and durl and drepo and stoken and dtoken and stat:
	 issues = get_issues(surl,stoken,srepo,stat)
	 post_issues(issues,durl,dtoken,drepo,stoken)
	else:
		click.echo("Parameter missing check for (s/d)url, (s/d)repo, (s/d)token, state(open/closed)")

#states [open,closed,all]
def get_issues(surl,stoken,srepo,stat):
	headers 	= {'Authorization':'token %s' % stoken}
	response	= requests.get("%s/repos/%s/issues?state=%s" % (surl,srepo,stat) ,headers=headers)
	result			= response.content
	issues 		= json.load(StringIO(result))
	return issues

def get_comments_on_issue(issue,stoken):
	headers={'Authorization':'token %s' % stoken}
	if issue.has_key("comments_url") and issue["comments_url"] is not None:
		response = requests.get("%s" % issue["comments_url"],headers=headers)
		result = response.content
		comments = json.load(StringIO(result))
		return result
	else :
		return []

def post_issues(issues,durl,dtoken,drepo,stoken):
	duri = "%s/repos/%s/issues" % (durl,drepo)
	for source in issues:
		if source.has_key("body") and source["body"] is not None:
			body = source["body"]
			title = source["title"]
		comments = get_comments_on_issue(source,stoken)
		works = ""
		if len(comments) > 2 :
			targets = json.load(StringIO(comments))
			for target in targets:
				works = works + "Comment Created-At " + target['created_at'] + " " + target['body']
		
		dest = {'title': source['title'],
										'body': body + works,
										'state': 'closed',
										'Content-Type': 'application/json',
										'Accept': 'application/json'}
		dheaders = {'Authorization':'token %s' % dtoken}
		res = requests.post("%s" % duri, headers=dheaders, data=json.dumps(dest))
		data = res.content
		res_issue = json.load(StringIO(data))
		click.echo("Successfully created issue %s" % res_issue["title"])
