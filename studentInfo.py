import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import MySQLdb as mysql
import re

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-h", "--host", dest="host", help="Enter db host")
    parser.add_option("-u", "--username", dest="username", help="Enter db username")
    parser.add_option("-p", "--password", dest="password", help="Enter db password")
    parser.add_option("-d", "--dbname", dest="dbname", help="Enter db dbname(will be created if does not exits)")
    (options, arguments) = parser.parse_args()
    return options

def incomplete_info():
    if(details['DOB'].get() in ('YYYY-MM-DD format only','')):
        mb.showerror(title='ERROR',message='could not add:\nINCOMPLETE INFORMATION',parent=root)
        return True
    dat = tuple(details.values())
    for x in dat[:-1]:
        if (x.get() == ''):
            mb.showerror(title='ERROR',message='could not add:\nINCOMPLETE INFORMATION',parent=root)
            return True
    return False


def no_table_open():
    if(table_name == ''):
        mb.showerror(title='ERROR',message='NO TABLE OPEN',parent=root)
        return True
    return False


def exit_file():
    if(mb.askyesno(title='EXIT',message='ARE YOU SURE YOU WANT TO EXIT?')):        
        root.destroy()

        
def reset_file():
    for x in details.values():
        x.set(value='')
    entries['DOB']['fg']='grey'
    x.set('YYYY-MM-DD format only')

def exit_table():
    global table_name
    table_name=''
    reset_file()

        
def delete_table():
    def del_given():
        tab_name=data.get()
        global table_name
        if(tab_name == ''):
            mb.showerror(title='ERROR',message='SELECT A TABLE',parent=del_window)
        else:
            if(table_name == tab_name):
                table_name = ''
                reset_file()
            cursor.execute('DROP TABLE '+tab_name)
            del_window.destroy()
        
    del_window = tk.Toplevel(root)
    del_window.grab_set()
    del_window.title('DELETE A TABLE')
    cursor.execute('SHOW TABLES')
    del_font = ('courier',-100,'bold')
    nrows = cursor.rowcount
    if(nrows == 0):
        no_tables=tk.Label(del_window,text='NO TABLES YET',font=del_font\
        ,bg='yellow',fg='black')
        close = tk.Button(del_window,text='close',bd=5,bg='red',\
        activebackground='blue',fg='black',activeforeground='white',font=myfont\
        ,cursor='hand2',command=del_window.destroy)
        no_tables.pack()
        close.pack()
        return
    
    rows,grid_row = cursor.fetchall(),0
    c = tk.Canvas(del_window)
    f = tk.Frame(c)
    vs = tk.Scrollbar(del_window,orient=tk.VERTICAL,command=c.yview)
    c.configure(yscrollcommand= vs.set)
    c.create_window((0,0),anchor='nw',window=f)
    f.bind('<Configure>',lambda e : c.configure(scrollregion=c.bbox('all')))
    
    data=tk.StringVar(value='')
    for x in rows:
        r=tk.Radiobutton(f,text=x[0],bg='yellow',fg='black',font=myfont\
        ,variable=data,value=x[0],tristatevalue='1')
        r.grid(row=grid_row,column=0,padx=10,pady=10)
        grid_row= grid_row+1
    del_b = tk.Button(del_window,text='delete',bd=5,bg='red',\
    activebackground='blue',fg='black',activeforeground='white',font=myfont\
    ,cursor='hand2',command=del_given)
    
    c.grid(row=0,column=0,padx=10,pady=10)
    vs.grid(row=0,column=1,padx=10,pady=10,sticky='ns')
    del_b.grid(row=1,column=0,padx=10,pady=10)
    


    
def create_table():
    def set_data(event):
        data.set(event.widget['text'])
    
    def create_given():
        tab_name = data.get()
        if(tab_name == ''):
            mb.showerror('ERROR','ENTER TABLE NAME!!',parent=create_window)
        elif(tab_name in [x[0] for x in rows]):
            mb.showerror('ERROR','TABLE ALREADY EXISTS',parent=create_window,)
        else:
            col=''
            for x in deets[:-1]:
                col+= x+' varchar(100) NOT NULL,'
            cursor.execute('CREATE TABLE '+tab_name+' (ENTRY int(10) NOT NULL AUTO_INCREMENT,'+col+'DOB date NOT NULL,PRIMARY KEY (`ENTRY`))')
            global table_name
            table_name  = tab_name
            reset_file()
            create_window.destroy()
        
    create_window = tk.Toplevel(root)
    create_window.title('CREATE A TABLE')
    create_window.grab_set()
    cursor.execute('SHOW TABLES')
    create_font = ('courier',-100,'bold')
    nrows,rows = cursor.rowcount,cursor.fetchall()
    data = tk.StringVar(value='')
    if(nrows == 0):
        no_tables=tk.Label(create_window,text='NO TABLES YET',font=create_font\
        ,bg='yellow',fg='black')
        no_tables.grid(row=0,column=0,padx=10,pady=10)
    else:
        grid_row =0
        c = tk.Canvas(create_window)
        f = tk.Frame(c)
        vs = tk.Scrollbar(create_window,orient=tk.VERTICAL,command=c.yview)
        c.configure(yscrollcommand= vs.set)
        c.create_window((0,0),anchor='nw',window=f)
        f.bind('<Configure>',lambda e : c.configure(scrollregion=c.bbox('all')))
        for x in rows:
            la=tk.Label(f,text=x[0],font=myfont,bg='yellow',fg='black')
            la.grid(row=grid_row,column=0,padx=10,pady=10)
            grid_row += 1
            la.bind('<Button>',set_data)
        c.grid(row=0,column=0,padx=10,pady=10)
        vs.grid(row=0,column=1,padx=10,pady=10,sticky='ns')
        
    entry_tab = tk.Entry(create_window,width=20,fg='blue',bg='white',font=myfont\
    ,textvariable=data)
    create_b = tk.Button(create_window,text='create',bd=5,bg='red',\
    activebackground='blue',fg='black',activeforeground='white',font=myfont\
    ,cursor='hand2',command=create_given)
    entry_tab.grid(row=1,column=0,padx=10,pady=10)
    create_b.grid(row=1,column=1,padx=10,pady=10)
    


def open_table():
    def open_given():
        global table_name
        if(table_name == data.get()):
            mb.showerror('ERROR','TABLE ALREADY OPEN',parent=open_window)
        elif(data.get() == ''):
            mb.showerror('ERROR','SELECT A TABLE',parent=open_window)
        else:
            table_name = data.get()
            open_window.destroy()
            cursor.execute('SELECT * FROM '+table_name+';')
            nrows = cursor.rowcount
            print(f'DETAILS STORED IN OPENDED TABLE ({table_name}):')
            if(nrows == 0):
                print('NO ENTRIES YET')
            else:
                var = ('ENTRY',)+deets
                rows = cursor.fetchall()
                for i in range(nrows):
                    for j in range(9):
                        print(var[j],':',rows[i][j])
                    print()
            reset_file()
        
    open_window = tk.Toplevel(root)
    open_window.title('OPEN A TABLE')
    open_window.grab_set()
    cursor.execute('SHOW TABLES;')
    open_font = ('courier',-100,'bold')
    nrows = cursor.rowcount
    if(nrows == 0):
        no_tables=tk.Label(open_window,text='NO TABLES YET',font=open_font\
        ,bg='yellow',fg='black')
        close = tk.Button(open_window,text='close',bd=5,bg='red',\
        activebackground='blue',fg='black',activeforeground='white',font=myfont\
        ,cursor='hand2',command=open_window.destroy)
        no_tables.pack()
        close.pack()
        return
    
    rows,grid_row = cursor.fetchall(),0
    data=tk.StringVar(value='')
    c = tk.Canvas(open_window)
    f = tk.Frame(c)
    vs = tk.Scrollbar(open_window,orient=tk.VERTICAL,command=c.yview)
    c.configure(yscrollcommand= vs.set)
    c.create_window((0,0),anchor='nw',window=f)
    f.bind('<Configure>',lambda e : c.configure(scrollregion=c.bbox('all')))
    for x in rows:
        r=tk.Radiobutton(f,text=x[0],bg='yellow',fg='black',font=myfont\
        ,variable=data,value=x[0],tristatevalue='1')
        r.grid(row=grid_row,column=0,padx=10,pady=10)
        grid_row= grid_row+1
    open_b = tk.Button(open_window,text='open',bd=5,bg='red',\
    activebackground='blue',fg='black',activeforeground='white',font=myfont\
    ,cursor='hand2',command=open_given)
    c.grid(row=0,column=0,padx=10,pady=10)
    vs.grid(row=0,column=1,padx=10,pady=10,sticky='ns')
    open_b.grid(row=1,column=0,padx=10,pady=10)
    

def add_entry():
    if(not no_table_open() and not incomplete_info()):
        values = tuple([x.get() for x in details.values()])
        col_names = '(FIRST_NAME,LAST_NAME,BRANCH,YEAR,GENDER,MOBILE,EMAIL,DOB)'
        cursor.execute('INSERT INTO '+table_name+' '+col_names+' VALUES '+str(values)+';')
        reset_file()

        
def delete_entries():
    if(no_table_open()):
        return
    
    def add_to_list(event):
        entryno = event.widget.grid_info()['row']
        if(str(entryno) not in del_var.get()):
            del_var.set(del_var.get()+str(entryno)+',')

    def do_delete():
        raw_del_list = re.findall(r'\d+',del_var.get())
        if(len(raw_del_list) == 0):
            mb.showerror('ERROR','NO ENTRIES GIVEN TO DELETE',parent=del_window)
            return
        del_list = [int(x) for x in raw_del_list]
        if(len(del_list) == 1):
            min_entry=del_list[0]
            cursor.execute('DELETE FROM '+table_name+' WHERE ENTRY = '+str(min_entry))
        else:
            min_entry = min(del_list)
            cursor.execute('DELETE FROM '+table_name+' WHERE ENTRY IN '+\
            str(tuple(del_list)))
        entry_set = min_entry
        cursor.execute('SELECT ENTRY FROM '+table_name+' WHERE ENTRY > '\
        +str(min_entry))
        for x in cursor.fetchall():
            cursor.execute('UPDATE '+table_name+' SET ENTRY = '+str(entry_set)+\
            ' WHERE ENTRY = '+str(x[0]))
            entry_set = entry_set + 1
        cursor.execute('ALTER TABLE '+table_name+' AUTO_INCREMENT='+str(entry_set))
            
            
    del_window = tk.Toplevel(root)
    del_window.title('DELETE ENTRIES')
    del_window.grab_set()
    cursor.execute('SELECT * FROM '+table_name+';')
    edit_font = ('courier',-100,'bold')
    nrows = cursor.rowcount
    if(nrows == 0):
        no_entries=tk.Label(del_window,text='NO ENTRIES YET',font=edit_font\
        ,bg='yellow',fg='black')
        close = tk.Button(del_window,text='close',bd=5,bg='red',\
        activebackground='blue',fg='black',activeforeground='white',font=myfont\
        ,cursor='hand2',command=del_window.destroy)
        no_entries.pack()
        close.pack()
    else:
        rows = cursor.fetchall()
        c = tk.Canvas(del_window,width=1200,height=400)
        f = tk.Frame(c)
        vs = tk.Scrollbar(del_window,orient=tk.VERTICAL,command=c.yview)
        hs = tk.Scrollbar(del_window,orient=tk.HORIZONTAL,command=c.xview)
        c.configure(yscrollcommand= vs.set)
        c.configure(xscrollcommand= hs.set)
        c.create_window((0,0),anchor='nw',window=f)
        f.bind('<Configure>',lambda e : c.configure(scrollregion=c.bbox('all')))
        
        data=[ [ tk.StringVar() for i in range(9)] for j in range(nrows) ]
        col_names = ('ENTRY',)+deets
        for j in range(9):
            l = tk.Label(f,text=col_names[j],font=myfont\
            ,bg='yellow',fg='black',width=10)
            l.grid(row=0,column=j,padx=10,pady=10)
        for i in range(1,nrows+1):
            #j=0
            e=tk.Entry(f,width=10,fg='blue',bg='white',font=myfont\
            ,textvariable=data[i-1][0],state=tk.DISABLED)
            data[i-1][0].set(str(i))
            e.grid(row=i,column=0,padx=10,pady=10)
            e.bind('<Button-1>',add_to_list)
            for j in range(1,9):
                e=tk.Entry(f,width=10,fg='blue',bg='white',font=myfont,\
                textvariable=data[i-1][j],state=tk.DISABLED)
                data[i-1][j].set(rows[i-1][j])
                e.grid(row=i,column=j,padx=10,pady=10)
                e.bind('<Button-1>',add_to_list)

        label_del=tk.Label(del_window,text="entries separated by anything except digits",font=myfont\
        ,bg='yellow',fg='black')
        del_var = tk.StringVar(value='')
        entry_del = tk.Entry(del_window,width=20,fg='blue',bg='white',font=myfont\
        ,textvariable=del_var) 
        delete = tk.Button(del_window,text='delete',bd=5,bg='red',\
        activebackground='blue',fg='black',activeforeground='white',font=myfont\
        ,cursor='hand2',command=do_delete)
        close = tk.Button(del_window,text='close',bd=5,bg='red',\
        activebackground='blue',fg='black',activeforeground='white',font=myfont\
        ,cursor='hand2',command=del_window.destroy)

        c.grid(row=0,column=0,padx=10,pady=10)
        vs.grid(row=0,column=1,padx=10,pady=10,sticky='ns')
        hs.grid(row=1,column=0,padx=10,pady=10,sticky='we')
        label_del.grid(row=2,column=0,padx=10,pady=10)
        entry_del.grid(row=3,column=0,padx=10,pady=10)
        delete.grid(row=4,column=0,padx=10,pady=10)
        close.grid(row=5,column=0,padx=10,pady=10)

    
def edit_table():
    if(no_table_open()):
        return
    
    #data to be considered
    def add_pos(event):
        info = event.widget.grid_info()
        point=(info['row']-1,info['column'])
        if( point not in pos ):
            pos.append(point)

    def update_table():
        for posi,posj in pos:
            if(data[posi][posj].get() == ''):
                data[posi][posj].set(rows[posi][posj])
            else:
                cursor.execute('UPDATE '+table_name+' SET '+deets[posj-1]+" = \'"+data[posi][posj].get()+"\' WHERE ENTRY = "+str(posi+1)+';')
                    
    edit_window = tk.Toplevel(root)
    edit_window.title('EDIT CURRENT TABLE')
    edit_window.grab_set()
    cursor.execute('SELECT * FROM '+table_name+';')
    edit_font = ('courier',-100,'bold')
    nrows = cursor.rowcount
    pos,i,j=[],0 ,0
    if(nrows == 0):
        no_entries=tk.Label(edit_window,text='NO ENTRIES YET',font=edit_font\
        ,bg='yellow',fg='black')
        close = tk.Button(edit_window,text='close',bd=5,bg='red',\
        activebackground='blue',fg='black',activeforeground='white',font=myfont\
        ,cursor='hand2',command=edit_window.destroy)
        no_entries.pack()
        close.pack()
    else:
        rows = cursor.fetchall()
        c = tk.Canvas(edit_window,width=1200,height=400)
        f = tk.Frame(c)
        vs = tk.Scrollbar(edit_window,orient=tk.VERTICAL,command=c.yview)
        hs = tk.Scrollbar(edit_window,orient=tk.HORIZONTAL,command=c.xview)
        c.configure(yscrollcommand= vs.set)
        c.configure(xscrollcommand= hs.set)
        c.create_window((0,0),anchor='nw',window=f)
        f.bind('<Configure>',lambda e : c.configure(scrollregion=c.bbox('all')))
        data=[ [ tk.StringVar() for i in range(9)] for j in range(nrows) ]
        col_names = ('ENTRY',)+deets
        for j in range(9):
            l = tk.Label(f,text=col_names[j],font=myfont\
            ,bg='yellow',fg='black',width=10)
            l.grid(row=0,column=j,padx=10,pady=10)
        for i in range(1,nrows+1):
            #j=0
            e=tk.Entry(f,width=10,fg='blue',bg='white',font=myfont\
            ,textvariable=data[i-1][0],state=tk.DISABLED)
            data[i-1][0].set(str(i))
            e.grid(row=i,column=0,padx=10,pady=10)
            for j in (1,2,6,7,8):
                e=tk.Entry(f,width=10,fg='blue',bg='white',font=myfont,\
                textvariable=data[i-1][j])
                data[i-1][j].set(rows[i-1][j])
                e.grid(row=i,column=j,padx=10,pady=10)
                e.bind('<Button-1>',add_pos)
            for j,val in ( (3,branch_val),(4,year_val),(5,gender_val) ):
                s=tk.Spinbox(f,values=val,textvariable=\
                data[i-1][j],width=10,fg='blue',bg='white',font=myfont)
                data[i-1][j].set(rows[i-1][j])
                s.grid(row=i,column=j,padx=10,pady=10)
                s.bind('<Button-1>',add_pos)
        update = tk.Button(edit_window,text='update',bd=5,bg='red',\
        activebackground='blue',fg='black',activeforeground='white',font=myfont\
        ,cursor='hand2',command=update_table)
        close = tk.Button(edit_window,text='close',bd=5,bg='red',\
        activebackground='blue',fg='black',activeforeground='white',font=myfont\
        ,cursor='hand2',command=edit_window.destroy)

        c.grid(row=0,column=0,padx=10,pady=10)
        vs.grid(row=0,column=1,padx=10,pady=10,sticky='ns')
        hs.grid(row=1,column=0,padx=10,pady=10,sticky='we')
        update.grid(row=2,column=0,padx=10,pady=10)
        close.grid(row=2,column=1,padx=10,pady=10)
        

def dob_active(event):
    if(details['DOB'].get() == 'YYYY-MM-DD format only'):
        event.widget['fg'] = 'blue'
        details['DOB'].set('')

arg = get_arguments() 
if((not arg.host) or (not arg.username) or (not arg.password) or (not arg.dbname)):
    print("enter all arguments.Use --help for more info")
    exit(-1)
    
root = tk.Tk()
root.title('STUDENT INFORMATION')
root.geometry('1500x1500')
myfont = ('courier',-20,'bold')
deets = ('FIRST_NAME','LAST_NAME','BRANCH','YEAR','GENDER','MOBILE','EMAIL','DOB')
branch_val= ('','EXTC','Computers','I.T.','Chemical','Biomedical','Bio-Tech')
year_val = ('','F.E.','S.E.','T.E.','B.E.')
gender_val=('','Male','Female')
details = {x:tk.StringVar(value='') for x in deets}
details['DOB'].set('YYYY-MM-DD format only')
table_name = ''

connection = mysql.connect(host = arg.host,user=arg.username,password=arg.password)
connection.autocommit(True)
cursor = connection.cursor()
cursor.execute(f'CREATE DATABASE IF NOT EXISTS {arg.dbname};')
cursor.execute(f'USE {arg.dbname};')


labels = {x:tk.Label(root,text=x,font=myfont,bg='yellow',fg='black')for x in deets}

entries = {x:tk.Entry(root,width=30,fg='blue',bg='white',font=myfont,textvariable\
=details[x])for x in('FIRST_NAME','LAST_NAME','MOBILE','EMAIL','DOB')}
entries['DOB']['fg'] = 'grey'
entries['DOB'].bind('<Button-1>',dob_active)


branch_spinbox = tk.Spinbox(root,values=branch_val,textvariable=\
details['BRANCH'],width=15,fg='blue',bg='white',font=myfont)

radio_buttons =\
{
'YEAR':[tk.Radiobutton(root,text=x,bg='yellow',fg='black',font=myfont,variable\
=details['YEAR'],value=x,tristatevalue='1') for x in ('F.E.','S.E.','T.E.','B.E.')],
'GENDER':[tk.Radiobutton(root,text=x,bg='yellow',fg='black',font=myfont,variable\
=details['GENDER'],value=x,tristatevalue='1') for x in ('male','female')]
}

reset = tk.Button(root,text='reset',bd=5,bg='red',activebackground='blue'\
,fg='black',activeforeground='white',font=myfont,cursor='hand2',command=reset_file)
add = tk.Button(root,text='add',bd=5,bg='red',activebackground='blue'\
,fg='black',activeforeground='white',font=myfont,cursor='hand2',command=add_entry)
edit = tk.Button(root,text='edit',bd=5,bg='red',activebackground='blue'\
,fg='black',activeforeground='white',font=myfont,cursor='hand2',command=edit_table)
delete = tk.Button(root,text='delete',bd=5,bg='red',activebackground='blue'\
,fg='black',activeforeground='white',font=myfont,cursor='hand2',command=delete_entries)


menubar = tk.Menu(root)
root.config(menu=menubar)
menu_File = tk.Menu(root,tearoff=0)
menu_File.add_command(label='Create Table',command = create_table)
menu_File.add_command(label='Open Table',command = open_table)
menu_File.add_command(label='Delete Table',command = delete_table)
menu_File.add_command(label='Exit Table',command = exit_table)
menu_File.add_separator()
menu_File.add_command(label='exit',command = exit_file)
menubar.add_cascade(label='File',menu=menu_File)

#placing all widgets (menu bar is already placed along with file menu)
labels['FIRST_NAME'].grid(row=0,column=0,padx=10,pady=40)
entries['FIRST_NAME'].grid(row=0,column=1,padx=10,pady=40)
labels['LAST_NAME'].grid(row=0,column=2,padx=10,pady=40)
entries['LAST_NAME'].grid(row=0,column=3,padx=10,pady=40)
labels['BRANCH'].grid(row=1,column=0,padx=10,pady=40)
branch_spinbox.grid(row=1,column=1,padx=10,pady=40)
labels['GENDER'].grid(row=1,column=2,padx=10,pady=40)
for i in range(2):
    radio_buttons['GENDER'][i].grid(row=1,column=i+3,padx=10,pady=40)
labels['YEAR'].grid(row=2,column=0,padx=10,pady=40)
for i in range(4):
    radio_buttons['YEAR'][i].grid(row=2,column=i+1,padx=10,pady=40)
labels['DOB'].grid(row=3,column=0,padx=10,pady=40)
entries['DOB'].grid(row=3,column=1,padx=10,pady=40)
labels['MOBILE'].grid(row=4,column=0,padx=10,pady=40)
entries['MOBILE'].grid(row=4,column=1,padx=10,pady=40)
labels['EMAIL'].grid(row=4,column=2,padx=10,pady=40)
entries['EMAIL'].grid(row=4,column=3,padx=10,pady=40)
reset.grid(row=5,column=0,padx=10,pady=40)
add.grid(row=5,column=1,padx=10,pady=40)
edit.grid(row=5,column=2,padx=10,pady=40)
delete.grid(row=5,column=3,padx=10,pady=40)
root.protocol('WM_DELETE_WINDOW',exit_file)
root.mainloop()
