from googlegantt import GanttChart, GanttCategory
from datetime import datetime
import random

gc = GanttChart('TestChart', width=1000, height=300)


n = 10
tasks = []

for i in range(100):

    dep = None if not tasks else random.sample(tasks, 1)[0]
    start_date = None if dep else datetime.now()
    t2 = gc.add_task('task%s' % i, start_date=start_date, depends_on=dep, duration=3)
    tasks.append(t2)


url = gc.get_url()
fn = 'chart.png'
image = gc.get_image(save_path=fn)

print url
print image

print('saved on %s' % fn)
