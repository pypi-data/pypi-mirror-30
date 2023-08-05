#!/usr/bin/env python3
import numpy as np
from os.path import getsize
__version__='1.4'
__author__='Blacksong'
class _zone_data(dict):
    def _setPlot3d_type(self):#文件格式为plot3d格式时运行这个函数  增加x,y,z,ptype这个变量 
        self.x=None
        self.y=None
        self.z=None
        self.ptype=None
        return self
    def rename(self,old,new):
        self[old]=self[new]
        self.pop(old)
    def set_data(self,names,values,attribute):
        self.names=names
        self.data=values
        self.attribute=attribute
        for i,v in zip(names,values):
            self[i]=v
    def __getitem__(self,k):
        if isinstance(k,str):
            return super().__getitem__(k)
        else:
            if self.attribute == 'fluent_prof':
                return self.data[:,k]
class class_read(dict):
    def __init__(self,filename,filetype=None,**kargs):
        self.fp=open(filename,'r')
        self.default_filetypes={'prof':'fluent_prof','dat':'tecplot_dat','out':'fluent_residual_out',
        'out2':'fluent_monitor_out','csv':'csv','txt':'txt','fmt':'plot3d','plot3d':'plot3d'}
        self.data=None
        if filetype is None:
            key=filename.split('.')[-1].lower()
            if key=='out':key=self.__recognize_out(self.fp)
            self.filetype=self.default_filetypes[key]
        else:
            self.filetype=filetype
        self.filesize=getsize(filename)
        if self.filetype=='tecplot_dat':
            self._read_dat()
        elif self.filetype=='fluent_prof':
            self._read_prof()
        elif self.filetype=='fluent_residual_out':
            self._read_out()
        elif self.filetype=='fluent_monitor_out':
            self.__read_out2()
        elif self.filetype=='csv':
            self.__read_csv(filename)
        elif self.filetype == 'plot3d':
            self.__read_plot3d(filename)
        self.fp.close()
    def __read_plot3d(self,filename):
        self.data=list()
        d=np.array(self.fp.read().split(),dtype='float64')
        n=int(d[0])
        shape=d[1:1+n*3].astype('int')
        start=1+n*3
        for i in range(n):
            zt,yt,xt=shape[i*3:i*3+3]
            block=_zone_data()._setPlot3d_type()
            block.x=d[start:start+xt*yt*zt]
            start+=xt*yt*zt
            block.y=d[start:start+xt*yt*zt]
            start+=xt*yt*zt
            block.z=d[start:start+xt*yt*zt]
            start+=xt*yt*zt
            block.ptype=d[start:start+xt*yt*zt].astype('int')
            start+=xt*yt*zt
            block.x.shape=(xt,yt,zt)
            block.y.shape=(xt,yt,zt)
            block.z.shape=(xt,yt,zt)
            block.ptype.shape=(xt,yt,zt)

            block.x=block.x.swapaxes(2,0)
            block.y=block.y.swapaxes(2,0)
            block.z=block.z.swapaxes(2,0)
            block.ptype=block.ptype.swapaxes(2,0)

            self[i]=block
            self.data.append(block)
    def __read_csv(self,filename):
        title=self.fp.readline()
        tmp=np.loadtxt(self.fp,dtype='float64',delimiter=',')
        title=title.strip().split(',')
        for i,j in enumerate(title):
            self[j]=tmp[:,i]
        self.data=tmp
    def __recognize_out(self,fp):
        fp.readline()
        t=fp.readline()
        t=t.split()
        key='out'
        if t:
            if t[0]=='"Iteration"':
                key='out2'
        fp.seek(0,0)
        return key
    def __read_out2(self):
        self.fp.readline()
        t=self.fp.readline()
        t=t.lstrip()[11:].strip()[1:-1]
        d=self.fp.read().encode().strip()
        d=d.split(b'\n')
        d=[tuple(i.split()) for i in d]
        x=np.array(d,dtype=np.dtype({'names':["Iteration",t],'formats':['int32','float64']}))
        self["Iteration"]=x['Iteration']
        self[t]=x[t]
        self.data=x
    def _read_out(self):#fluent residual file
        items=[]
        items_n=0
        data=[]
        iter_pre='0'
        time_index=False
        for i in self.fp:
            if i[:7]=='  iter ':
                if items_n!=0:continue
                j=i.strip().split()
                items.extend(j)
                if items[-1]=='time/iter':
                    items.pop()
                    items.extend(('time','iter_step'))
                    time_index=True
                items_n=len(items)
            if items_n==0:continue
            else:
                j=i.split()
                if len(j)==items_n:
                    if j[0].isdigit():
                        if j[0]==iter_pre:continue
                        iter_pre=j[0]
                        if time_index:j.pop(-2)
                        data.append(tuple(j))
        if time_index:items.pop(-2)
        a=np.array(data,dtype=np.dtype({'names':items,'formats':['i']+['f']*(len(items)-2)+['i']}))
        for i,k in enumerate(items):
            self[k]=a[k]
        self.data=a
    def _read_prof(self):
        fp=self.fp
        d=fp.read()
        d=d.replace('\r','')
        d=d.split('((')
        d.pop(0)
        data=[]
        def read(x):
            x=x.split('(')
            title=x[0].split()[0]
            x.pop(0)
            data=[]
            name=[]
            ii=0
            for i in x:
                c=i.split('\n')
                ii+=1
                name.append(c[0])
                data.append(c[1:-2])
            data[-1].pop()
            values=np.array(data,dtype='float32')
            if len(values)!=len(name):return False
            t=_zone_data()
            t.set_data(name,values,self.filetype)
            return title,t
        for i in d:
            k,v=read(i)
            self[k]=v
    def parse_zone(self):
        fp=self.fp
        t=fp.readline().rstrip()
        if t[:4]!='ZONE':
            return False
            raise EOFError('wrong file type!')
        title=t[t.find('"')+1:-1].strip()
        n=title.find('Step ')
        if n!=-1:title=title[:n].strip()
        attr={}
        while True:
            t=fp.readline().strip()
            if t[:2]=='DT':break
            t=t.replace(',',' ').split()
            for i in t:
                k,v=i.split('=')
                if v.isdigit():v=int(v)
                attr[k]=v
        if t.find('SINGLE')==-1:
            raise EOFError('file type error')
        t=t[t.find('(')+1:t.find(')')].strip().split()
        attr['DT']=tuple(t)
        return title,attr
    def _read_dat(self):
        fp=self.fp
        t=fp.readline().rstrip()
        self.title=t[t.find('"')+1:-1]
        t=fp.readline().rstrip()
        self.variables=[t[t.find('"')+1:-1]]
        while True:
            i=fp.readline()
            t=i.strip()
            if t[0]!='"':break
            pos=fp.tell()
            t=t[t.find('"')+1:-1]
            n=t.find('Dataset:')
            if n!=-1:
                t=t[:n].strip()
            self.variables.append(t)
        fp.seek(pos)
        self.variables=tuple(self.variables)
        a=[]
        while True:
            t=self.parse_zone()
            if t is False:
                break
            a.append(t)
            t=self._read_data(t)
        self.zones={i[0]:i[1] for i in a}
    def _read_data(self,a):
        fp=self.fp
        title,attribute=a
        zo=_zone_data()
        self[title]=zo
        if 'Nodes' in attribute and 'Elements' in attribute:
            n=attribute['Nodes']
            # self.now_keys={k:d[i*n:i*n+n] for i,k in enumerate(self.parent.variables)}
            m=attribute['Elements']
            nn=n//5
            if n%5>0:nn=int(nn+1)
            for j,key in enumerate(self.variables):
                ii=0
                s=[]
                for i in fp:
                    s.append(i)
                    ii+=1
                    if ii==nn:break
                if attribute['DT'][j]=='SINGLE':
                    ddtype='float32'
                else:
                    raise EOFError('DT type wrong!')
                zo[key]=np.array(''.join(s).split(),dtype=ddtype)
            s=[]
            for i in fp:
                s.append(i.split())
                m-=1
                if m==0:break
            zo['ELEMENTS']=np.array(s,dtype='int32')
        return True
    def __getitem__(self,k):
        if isinstance(k,str):
            return super().__getitem__(k)
        else:return self.data[k]
    def rename(self,old,new):
        self[new]=self[old]
        self.pop(old)
    def write(self,filename):
        write(self,filename)
class data_ndarray(np.ndarray):
	def write(self,filename):
		write(self,filename)
	def setfiletype(self,filetype):
		self.filetype=filetype
def read(filename,filetype=None,**kargs):
	ext=filename.split('.')[-1].lower()
	if ext=='txt':
		data = [i.split() for i in open(filename) if i.lstrip() and i.lstrip()[0]!='#']
		data=np.array(data,dtype='float64')
		data=data_ndarray(data.shape,dtype=data.dtype,buffer=data.data)
		data.setfiletype('txt')
	else:
		data=class_read(filename)
	return data
class write:
    def __init__(self,data,filename,filetype=None):
        default_filetypes={'prof':'fluent_prof','dat':'tecplot_dat','out':'fluent_residual_out',
        'out2':'fluent_monitor_out','csv':'csv','txt':'txt','fmt':'plot3d','plot3d':'plot3d'}
        ext=filename.split('.')[-1].lower()
        if filetype is None:
            filetype=default_filetypes.get(ext,None)
        if filetype is None:
            filetype=data.filetype

        if filetype=='fluent_prof':
            self.__write_prof(data,filename)
        elif filetype=='tecplot_dat':
            self.__write_dat(data,filename)
        elif filetype=='csv':
            self.__write_csv(data,filename)
        elif filetype=='fluent_monitor_out':
            self.__write_out2(data,filename)
        elif filetype=='fluent_residual_out':
            self.__write_out(data,filename)
        elif filetype=='txt':
        	np.savetxt(filename,data)
        elif filetype=='plot3d':
            self.__write_plot3d(data,filename)
        else:
            raise EOFError('file type error!')

    def __write_plot3d(self,data,filename):
        fp=open(filename,'w')
        def writelines(ffp,write_data,line_max):
            ffp.write('\n')
            n_line=int(write_data.size/line_max)
            write_data.reshape((-1,n_line))
            s=write_data.astype('U')[:n_line*line_max]
            s.resize((n_line,line_max))
            s_lines=[' '.join(i) for i in s]
            ffp.write('\n'.join(s_lines))
            n = write_data.size-n_line*line_max
            if n:
                ffp.write('\n'+ ' '.join(write_data[-n:]))
        shape=list()
        for i,v in enumerate(data.data):
            shape.extend(v.x.shape)

        fp.write(str(i+1)+'\n')
        fp.write(' '.join([str(i) for i in shape]))
        for i,v in enumerate(data.data):
            x=v.x.swapaxes(0,2)
            x.resize(x.size)
            y=v.y.swapaxes(0,2)
            y.resize(y.size)
            z=v.z.swapaxes(0,2)
            z.resize(z.size)
            p=v.ptype.swapaxes(0,2)
            p.resize(p.size)
            writelines(fp,x,5)
            writelines(fp,y,5)
            writelines(fp,z,5)
            writelines(fp,p,5)

    def __write_out(self,data,filename):
        fp=open(filename,'w')
        self.__write_delimiter(data,fp,'  ',title_format='',specified_format=' %d',specified_titles=['iter'],other_format='%.8e')
        fp.close()
    def __write_out2(self,data,filename):
        fp=open(filename,'w')
        value=[i for i in data.keys() if i!='Iteration'][0]
        fp.write('"Convergence history of %s"\n' % value)
        self.__write_delimiter(data,fp,' ',title_format='"',specified_format='%d',specified_titles=['Iteration'])
        fp.close()
    def __write_csv(self,data,filename):
        fp=open(filename,'w')
        self.__write_delimiter(data,fp,',')
        fp.close()
    def __write_delimiter(self,data,fp,delimiter,title_format='',specified_format='',specified_titles=[],other_format='%.15e'):
        other_titles=[i for i in data.keys() if i not in specified_titles]
        title=specified_titles+other_titles
        title_w=[title_format+i+title_format for i in title]
        fp.write(delimiter.join(title_w)+'\n')
        s=np.vstack([data[i] for i in title]).T
        data_format=specified_format+delimiter+delimiter.join([other_format]*len(other_titles))+'\n'
        for i in s:
            fp.write(data_format % tuple(i))
    def __write_prof(self,data,filename):
        fp=open(filename,'wb')
        for i in data.keys():
            keys=list(data[i].keys())
            keys.sort()
            keys.sort(key=lambda x:len(x))
            n=len(data[i][keys[0]])
            fs='(('+i+' point '+str(n)+')\n'
            fp.write(fs.encode())
            for k in keys:
                fs='('+k+'\n'
                fp.write(fs.encode())
                [fp.write((str(j)+'\n').encode()) for j in data[i][k]]
                fp.write(')\n'.encode())
            fp.write(')\n'.encode())
    def __write_dat(self,data,filename):
        if 'Nodes' in attribute and 'Elements' in attribute:
            pass
if __name__=='__main__':
    from matplotlib import pyplot as plt
    a=read('se.fmt')
    b=read('xyz.fmt')
    for i in a:
        r=a[i].x-b[i].x
        print(r.any())
        r=a[i].y-b[i].y
        print(r.any())
        r=a[i].z-b[i].z
        print(r.any())
        r=a[i].ptype-b[i].ptype
        print(r.any())