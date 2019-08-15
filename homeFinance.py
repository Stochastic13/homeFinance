from crypto_funcs import new_db, decrypt_db, encrypt_db
import os
from tkinter import ttk, scrolledtext
from tkinter import *
import sys
import time
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.gridspec import GridSpec

# check if creating a new database or using old one
new = True
mainfile = None
p = None
dbpath = None  # These four lines are to remove pycharm flagging upcoming lines as a warning
if len(sys.argv) < 2:
    new = True
elif len(sys.argv) == 2:
    dbpath = os.getcwd() + '\\' + sys.argv[1]
    new = False  # Using old one
else:
    print('Too many arguments given.')
    quit(1)

if new:
    new_db()
    print('Restart to begin')
    quit(0)
else:
    mainfile, p = decrypt_db(dbpath)

# parsing the data into a pandas dataframe
metadata = mainfile.decode().split('\n')[0].split(',')
# printing basic stats
print('Database created at: ' + time.asctime(time.localtime(float(metadata[0]))))
print('Database last opened at: ' + time.asctime(time.localtime(float(metadata[3]))))
print('Total Transactions: ' + metadata[1])
df = mainfile.decode().split('\n')[1:]
df = [x.split(',') for x in df]
if len(df) == 1:
    df = []
df = pd.DataFrame.from_records(data=df,
                               columns=['SerialID', 'Date', 'Type', 'From', 'To', 'Category', 'Amount', 'Comments'])
categories = metadata[2].split(':')[0].split(';')
accounts = metadata[2].split(':')[1].split(';')
payees = metadata[2].split(':')[2].split(';')
t_count = int(metadata[1])
assert t_count == df.shape[0], "Corrupt metadata or database size mismatch."
t_last = metadata[3]


def entryvalidate(event=None):  # to validate date entered in date1
    val = date1.get()
    try:
        t = time.strptime(val, '%d/%m/%y')
        valid_entry.set(
            '1' + valid_entry.get()[1])  # to allow for checking if the date/amt is correct before submitting
        date1.config(bg='#d0f5c9')  # change color based on valid or invalid (same for similar functions)
    except ValueError:
        date1.delete(0, END)
        date1.config(bg='#f2b7b3')
        valid_entry.set('0' + valid_entry.get()[1])


def entryvalidate2(event=None):  # to validate date entered in date2
    val = amount.get()
    try:
        t = float(val)
        valid_entry.set(valid_entry.get()[0] + '1')
        amount.config(bg='#d0f5c9')
    except ValueError:
        amount.delete(0, END)
        amount.config(bg='#f2b7b3')
        valid_entry.set(valid_entry.get()[0] + '0')


def new_transaction(event=None):  # submit new transaction
    global t_count
    entryvalidate2()  # check the date and amount
    if valid_entry.get() != '11':
        submit_button.config(state=DISABLED, text='Improper entry')
        root.after(3000, lambda: submit_button.config(state=NORMAL, text='Submit!'))
    else:
        newrow = [str(t_count), date1.get(), var_type.get(), var_from.get(), var_to.get(), var_category.get(),
                  amount.get(), comments.get()]
        df.loc[t_count] = newrow
        t_count += 1
        date1.delete(0, END)
        date1.insert(0, time.strftime('%d/%m/%y', time.localtime()))
        entryvalidate()
        amount.delete(0, END)
        entryvalidate2()
        comments.delete(0, END)
        submit_button.config(state=DISABLED, text='Success!!')
        root.after(3000, lambda: submit_button.config(state=NORMAL, text='Submit!'))
        numeric_analyze()  # recompute the analysis


def menu_alter(*event_data):  # change the menu in the "To" section based on "type" and after additions/deletions
    if var_type.get() == 'Transfer':  # then "To" should have accounts
        var_to.set('')
        to_m['menu'].delete(0, END)
        for i in accounts:
            to_m['menu'].add_command(label=i, command=lambda x=i: var_to.set(x))
        var_to.set(accounts[0])
    else:
        var_to.set('')
        to_m['menu'].delete(0, END)
        for i in payees:
            to_m['menu'].add_command(label=i, command=lambda x=i: var_to.set(x))
        var_to.set(payees[0])


def add_payee(event=None):  # add a new payee (similar functions named in a self-explanatory way)
    payees.append(new_payee.get())
    new_payee.delete(0, END)
    del_sel.set('')
    del_payee['menu'].delete(0, END)
    for i in payees:
        del_payee['menu'].add_command(label=i, command=lambda x=i: del_sel.set(x))
    b_new_payee.config(state=DISABLED, text='Success!!')
    root.after(2000, lambda: b_new_payee.config(state=NORMAL, text='Add New Payee'))
    menu_alter()
    view_repopulate()


def rem_payee(event=None):
    payees.remove(del_sel.get())
    del_payee['menu'].delete(0, END)
    del_sel.set('')
    for i in payees:
        del_payee['menu'].add_command(label=i, command=lambda x=i: del_sel.set(x))
    b_del_payee.config(state=DISABLED, text='Success!')
    root.after(2000, lambda: b_del_payee.config(state=NORMAL, text='Delete Payee'))
    menu_alter()
    view_repopulate()


def add_category(event=None):
    categories.append(new_category.get())
    new_category.delete(0, END)
    del_sel_cat.set('')
    del_category['menu'].delete(0, END)
    category_m['menu'].delete(0, END)
    for i in categories:
        del_category['menu'].add_command(label=i, command=lambda x=i: del_sel_cat.set(x))
        category_m['menu'].add_command(label=i, command=lambda x=i: var_category.set(x))
    b_new_category.config(state=DISABLED, text='Success!!')
    root.after(2000, lambda: b_new_category.config(state=NORMAL, text='Add New Category'))
    view_repopulate()


def rem_category(event=None):
    categories.remove(del_sel_cat.get())
    del_sel_cat.set('')
    del_category['menu'].delete(0, END)
    category_m['menu'].delete(0, END)
    for i in categories:
        del_category['menu'].add_command(label=i, command=lambda x=i: del_sel_cat.set(x))
        category_m['menu'].add_command(label=i, command=lambda x=i: var_category.set(x))
    var_category.set(categories[0])
    b_del_category.config(state=DISABLED, text='Success!!')
    root.after(2000, lambda: b_del_category.config(state=NORMAL, text='Delete Category'))
    view_repopulate()


def add_account(event=None):
    accounts.append(new_account.get())
    new_account.delete(0, END)
    del_sel_acc.set('')
    del_account['menu'].delete(0, END)
    from_m['menu'].delete(0, END)
    for i in accounts:
        del_account['menu'].add_command(label=i, command=lambda x=i: del_sel_acc.set(x))
        from_m['menu'].add_command(label=i, command=lambda x=i: var_from.set(x))
    b_new_account.config(state=DISABLED, text='Success!!')
    root.after(2000, lambda: b_new_account.config(state=NORMAL, text='Add New Account'))
    menu_alter()
    view_repopulate()


def rem_account(event=None):
    accounts.remove(del_sel_acc.get())
    del_sel_acc.set('')
    del_account['menu'].delete(0, END)
    from_m['menu'].delete(0, END)
    for i in accounts:
        del_account['menu'].add_command(label=i, command=lambda x=i: del_sel_acc.set(x))
        from_m['menu'].add_command(label=i, command=lambda x=i: var_from.set(x))
    var_from.set(accounts[0])
    b_del_account.config(state=DISABLED, text='Success!!')
    root.after(2000, lambda: b_del_account.config(state=NORMAL, text='Delete Account'))
    menu_alter()
    view_repopulate()


def view_refresh(event=None):  # refresh the view in the View tab (after a new filtering)
    viewmain.config(state=NORMAL)
    sel_type = list_type.curselection()
    sel_account = list_account.curselection()
    sel_category = list_category.curselection()
    sel_payee = list_payee.curselection()
    val_type = []
    for i in sel_type:
        val_type.append(list_type.get(i))
    val_account = []
    for i in sel_account:
        val_account.append(list_account.get(i))
    val_category = []
    for i in sel_category:
        val_category.append(list_category.get(i))
    val_payee = []
    for i in sel_payee:
        val_payee.append(list_payee.get(i))
    main_bool = np.array(np.ones((df.shape[0])), dtype=bool)
    if len(val_type) < list_type.size():
        main_bool = np.logical_and(main_bool, df['Type'].isin(val_type).to_numpy())
    if len(val_account) < list_account.size():
        main_bool = np.logical_and(main_bool, df['From'].isin(val_account).to_numpy())
    if (len(val_payee) < list_payee.size()) and ('Transfer' not in val_type):
        main_bool = np.logical_and(main_bool, df['To'].isin(val_payee).to_numpy())
    if (len(val_payee) < list_payee.size()) and ('Transfer' in val_type):
        main_bool[df['Type'] != 'Transfer'] = np.logical_and(main_bool, df['To'].isin(val_payee).to_numpy())[
            df['Type'] != 'Transfer']
        main_bool[df['Type'] == 'Transfer'] = np.logical_and(main_bool, df['To'].isin(val_account).to_numpy())[
            df['Type'] == 'Transfer']
    if len(val_category) < list_category.size():
        main_bool = np.logical_and(main_bool, df['Category'].isin(val_category).to_numpy())
    date_valid = np.array([True if ((time.mktime(time.strptime(x, '%d/%m/%y')) >= time.mktime(
        time.strptime(date_range_1.get(), '%d/%m/%y'))) and (time.mktime(time.strptime(x, '%d/%m/%y')) <= time.mktime(
        time.strptime(date_range_2.get(), '%d/%m/%y')))) else False for x in df['Date'].to_numpy()])
    main_bool = np.logical_and(main_bool, date_valid)
    string_final = '{:^5s}{:^10s}{:^20s}{:^20s}{:^20s}{:^20s}{:^15s}{:^40s}'.format(
        *['ID', 'Date', 'Type', 'From', 'To', 'Category', 'Amount', 'Comments'])
    string_final += '\n' + ('_' * 150) + '\n'
    for x, y in df.loc[main_bool, :].iterrows():
        string_final = string_final + '{:^5s}{:^10s}{:^20s}{:^20s}{:^20s}{:^20s}{:^15s}{:40s}'.format(
            *[str(z) for z in y.to_list()]) + '\n'
    viewmain.delete(1.0, END)
    viewmain.insert(1.0, string_final)
    viewmain.config(state=DISABLED)


def view_repopulate():
    list_account.delete(0, END)
    list_category.delete(0, END)
    list_payee.delete(0, END)
    for i in accounts:
        list_account.insert(END, i)
    for i in categories:
        list_category.insert(END, i)
    for i in payees:
        list_payee.insert(END, i)
    list_type.select_set(0, END)
    list_account.select_set(0, END)
    list_category.select_set(0, END)
    list_payee.select_set(0, END)


def entryvalidate3(event=None):  # to validate date entered
    val = date_range_1.get()
    try:
        t = time.strptime(val, '%d/%m/%y')
        date_range_1.config(bg='#d0f5c9')
    except ValueError:
        date_range_1.delete(0, END)
        date_range_1.config(bg='#f2b7b3')


def entryvalidate4(event=None):  # to validate date entered
    val = date_range_2.get()
    try:
        t = time.strptime(val, '%d/%m/%y')
        date_range_2.config(bg='#d0f5c9')
    except ValueError:
        date_range_2.delete(0, END)
        date_range_2.config(bg='#f2b7b3')


def numeric_analyze(event=None):  # analyze and summarize the data numericaly
    df['Amount'] = df['Amount'].astype(float)  # change the types of the dataframe
    dates = np.array([time.mktime(time.strptime(x, '%d/%m/%y')) for x in df['Date'].to_numpy()])
    try:  # validate date format
        start = time.mktime(time.strptime(date_start.get(), '%d/%m/%y'))
        end = time.mktime(time.strptime(date_end.get(), '%d/%m/%y'))
    except:
        analyze.config(state=DISABLED, text='Incorrect!')
        root.after(2000, lambda: analyze.config(state=NORMAL, text='Analyze!'))
        return
    df_sub = df.loc[np.logical_and(dates >= start, dates <= end), :]  # the relevant part based on dates
    df_start = df.loc[dates < start, :]  # to compute the opening balance
    tots = ['Total', 0, 0, 0, 0, 0, 0]  # for the total_labels
    labs = ['', '', '', '', '', '', '', '']  # text for the major_labels
    payeestm = np.array([0 for z in payees], dtype=float)  # total for each payee in Minus transactions
    payeestp = np.array([0 for z in payees], dtype=float)  # same as above for Plus
    for i in accounts:
        labs[0] += (i + '\n')
        df_spec = df_start.loc[df_start['From'] == i, :]
        opening = (-np.sum(df_spec.loc[df_spec['Type'].isin(['Transfer', 'Minus']), 'Amount']) + np.sum(
            df_spec.loc[df_spec['Type'] == 'Plus', 'Amount']) + np.sum(
            df_start.loc[np.logical_and(df_start['To'] == i, df_start['Type'] == 'Transfer'), 'Amount']))
        labs[1] += str(opening) + '\n'
        df_spec2 = df_sub.loc[df_sub['From'] == i, :]
        cnt = (df_spec2.shape[0] + df_sub.loc[np.logical_and(df_sub['Type'] == 'Transfer', df_sub['To'] == i)].shape[0])
        labs[2] += str(cnt) + '\n'
        diff = (-np.sum(df_spec2.loc[df_spec2['Type'].isin(['Transfer', 'Minus']), 'Amount']) + np.sum(
            df_spec2.loc[df_spec2['Type'] == 'Plus', 'Amount']) + np.sum(
            df_sub.loc[np.logical_and(df_sub['To'] == i, df_sub['Type'] == 'Transfer'), 'Amount']))
        labs[4] += str(diff) + '\n'
        labs[3] += str(opening + diff) + '\n'
        tots[1] += opening
        tots[2] += cnt
        tots[3] += (opening + diff)
        tots[4] += diff
        payeesm = []
        payeesp = []
        for j in payees:
            payeesp.append(
                np.sum(df_spec2.loc[np.logical_and(df_spec2['To'] == j, df_spec2['Type'] == 'Plus'), 'Amount']))
            payeesm.append(np.sum(df_spec2.loc[np.logical_and(df_spec2['To'] == j,
                                                              df_spec2['Type'].isin(['Minus', 'Transfer'])), 'Amount']))
        payeestm += np.array(payeesm)
        payeestp += np.array(payeesp)
        labs[5] += payees[np.argmax(payeesm)] + '\n'
        labs[6] += payees[np.argmax(payeesp)] + '\n'
    major_label_1.config(text=labs[0])
    major_label_2.config(text=labs[1])
    major_label_3.config(text=labs[2])
    major_label_4.config(text=labs[3])
    major_label_5.config(text=labs[4])
    major_label_6.config(text=labs[5])
    major_label_7.config(text=labs[6])
    major_label_8.config(text=labs[7])
    total_label_2.config(text=str(tots[1]), fg=['#02630c', '#870309'][int(tots[1] < 0)])
    total_label_3.config(text=str(tots[2]))
    total_label_4.config(text=str(tots[3]), fg=['#02630c', '#870309'][int(tots[3] < 0)])
    total_label_5.config(text=str(tots[4]), fg=['#02630c', '#870309'][int(tots[4] < 0)])
    total_label_6.config(text=payees[np.argmax(payeestm)])
    total_label_7.config(text=payees[np.argmax(payeestp)])
    (_, idx, counts) = np.unique(
        df_sub.loc[:, 'Category'].to_numpy(), return_index=True,
        return_counts=True)
    if len(counts) > 0:
        index = idx[np.argmax(counts)]
        total_label_8.config(text=df_sub.loc[:, 'Category'].to_numpy()[index])
    else:
        total_label_8.config(text='-')
    for tag in payee_numeric.tag_names():
        payee_numeric.tag_delete(tag)
    for tag in category_numeric.tag_names():
        category_numeric.tag_delete(tag)
    payee_numeric.config(state=NORMAL)
    payee_numeric.delete(1.0, END)
    payee_numeric.insert(1.0, ' ' * 10)
    payee_numeric.insert(END, '       Payee        ')
    payee_numeric.insert(END, ' ' * 5)
    payee_numeric.insert(END, 'Total Transaction \n')
    payee_numeric.insert(END, ''.join(['_'] * (18 * 4)))
    x = 0
    for i in payees:
        payee_numeric.insert(END, ' ' * 10)
        payee_numeric.insert(END, '{:^20s}'.format(i))
        payee_numeric.insert(END, ' ' * 5)
        payee_numeric.insert(END, str(payeestp[x] - payeestm[x]) + '\n', i)
        payee_numeric.tag_config(i, foreground=['#02630c', '#870309'][(payeestp[x] - payeestm[x]) < 0])
        x += 1
    payee_numeric.config(state=DISABLED)
    category_numeric.config(state=NORMAL)
    category_numeric.delete(1.0, END)
    category_numeric.insert(1.0, ' ' * 10)
    category_numeric.insert(END, '      Category      ')
    category_numeric.insert(END, ' ' * 5)
    category_numeric.insert(END, 'Total Transaction \n')
    category_numeric.insert(END, ''.join(['_'] * (18 * 4)))
    x = 0
    for i in categories:
        category_numeric.insert(END, ' ' * 10)
        category_numeric.insert(END, '{:^20s}'.format(i))
        category_numeric.insert(END, ' ' * 5)
        val = -np.sum(df_sub.loc[np.logical_and(df_sub['Type'] == 'Minus', df_sub['Category'] == i), 'Amount'])
        val += np.sum(df_sub.loc[np.logical_and(df_sub['Type'] == 'Plus', df_sub['Category'] == i), 'Amount'])
        category_numeric.insert(END, str(val) + '\n', i)
        category_numeric.tag_config(i, foreground=['#02630c', '#870309'][(val) < 0])
        x += 1
    category_numeric.config(state=DISABLED)


def foo_plot(x, df_main, end, start, dates):
    d1 = {'Payee': 'To', 'Category': 'Category', 'Account': 'From'}
    d2 = {'Payee': payees, 'Category': categories, 'Account': accounts}
    gs = GridSpec(2, 2)
    gs.update(hspace=0.05)
    ax1 = mainfig.add_subplot(gs[0, 0])
    ax2 = mainfig.add_subplot(gs[0, 1])
    ax3 = mainfig.add_subplot(gs[1, :])
    val_minus = []
    val_plus = []
    for i in d2[x]:
        val_minus.append(
            np.sum(df_main.loc[np.logical_and(df_main[d1[x]] == i, df_main['Type'] == 'Minus'), 'Amount']))
        val_plus.append(
            np.sum(df_main.loc[np.logical_and(df_main[d1[x]] == i, df_main['Type'] == 'Plus'), 'Amount']))
    vals_plot_m = np.array(val_minus)[np.array(val_minus) > 0]
    cats_plot_m = np.array(d2[x])[np.array(val_minus) > 0]
    if len(vals_plot_m) > 9:
        temp = vals_plot_m.sort()
        temp = (vals_plot_m >= temp[-9])
        vals_plot_m = vals_plot_m[temp] + [np.sum(vals_plot_m[np.logical_not(temp)])]
        cats_plot_m = cats_plot_m[temp] + ['Others']
    vals_plot_p = np.array(val_plus)[np.array(val_plus) > 0]
    cats_plot_p = np.array(d2[x])[np.array(val_plus) > 0]
    if len(vals_plot_p) > 9:
        temp = vals_plot_p.sort()
        temp = (vals_plot_p >= temp[-9])
        vals_plot_p = vals_plot_p[temp] + [np.sum(vals_plot_p[np.logical_not(temp)])]
        cats_plot_p = cats_plot_p[temp] + ['Others']
    wedges, texts = ax1.pie(vals_plot_m)
    ax1.legend(wedges, cats_plot_m, loc='center left', title='Legend', bbox_to_anchor=(1, 0, 0.5, 1))
    ax1.set_title(x + ' for Minus')
    wedges, texts = ax2.pie(vals_plot_p)
    ax2.legend(wedges, cats_plot_p, loc='center left', title='Legend', bbox_to_anchor=(1, 0, 0.5, 1))
    ax2.set_title(x + ' for Plus')
    if (end - start) / 3600 / 24 / 7 >= 2:
        yvals = []
        cutoffs = [start + j * 7 * 24 * 3600 for j in range(int(round((end - start) / 3600 / 24 / 7)))]
        for i in d2[x]:
            subtemp = []
            for j in range(len(cutoffs)):
                sel = np.logical_and((df_main.loc[:, d1[x]] == i), np.array(dates >= cutoffs[j]))
                sel = np.logical_and(sel, np.array(dates < (cutoffs[j] + 7 * 24 * 3600)))
                df_temp = df_main.loc[sel, :]
                subtemp.append(
                    np.sum(df_temp.loc[df_temp['Type'] == status_graph_v.get().split('Focus on ')[1], 'Amount']))
            yvals.append(subtemp[:])
        summedcats = np.array(np.sum(np.array(yvals), axis=1))
        temp = [True for x in d2[x]]
        if len(summedcats) > 9:
            temp = np.logical_and((summedcats >= (np.sort(summedcats)[-9])), (summedcats > 0))
            yvalsnew = np.array(yvals)[temp, :]
        else:
            yvalsnew = np.array(yvals)
        with np.errstate(divide='ignore', invalid='ignore'):
            yvalsnew[yvalsnew > 0] = (np.array(yvalsnew) / np.sum(np.array(yvalsnew), axis=0) * 100)[yvalsnew > 0]
        polys = ax3.stackplot(np.arange(0, len(cutoffs)), yvalsnew)
        ax3.set_title(x + '-wise money flow ' + status_graph_v.get().split('Focus on ')[1] + ' over time')
        ax3.set_xticklabels(['Week ' + str(j) for j in range(len(cutoffs))])
        ax3.set_ylabel('Percentage')
        ax3.set_ylim(0, 100)
        ax3.legend(polys, np.array(d2[x])[temp].tolist() + ['Others'], loc='upper center',
                   bbox_to_anchor=(0.5, -0.08), ncol=min((np.sum(temp) + 1), 9))


def foo_time(df_early, df_main, end, start, dates):
    accs = [[] for i in accounts]
    xtimes = [[] for i in accounts]
    total = [0]
    xtotal = [0]
    for i in range(len(accounts)):
        accs[i].append(np.sum(df_early.loc[np.logical_and(df_early['Type'] == 'Plus', df_early['From'] == i), 'Amount']) - np.sum(df_early.loc[np.logical_and(df_early['Type'] == 'Minus', df_early['From'] == i), 'Amount']))
        xtimes[i].append(0)
        total[0] += accs[i][-1]
    df_main.loc[:, 'Date'] = dates.astype(float)
    df_main.sort_values('Date', ascending=True, inplace=True)
    for j, i in df_main.iterrows():
        if i[2] != 'Transfer':
            ind = accounts.index(i[3])
            accs[ind].append(accs[ind][-1] + {'Minus':-1, 'Plus':1}[i[2]] * i[6])
            xtimes[ind].append((i[1] - start)/24/3600)
            total.append(total[-1] + {'Minus':-1, 'Plus':1}[i[2]] * i[6])
            xtotal.append((i[1] - start)/24/3600)
        else:
            ind = accounts.index(i[3])
            accs[ind].append(accs[ind][-1] - i[6])
            xtimes[ind].append((i[1] - start) / 24 / 3600)
            ind = accounts.index(i[4])
            accs[ind].append(accs[ind][-1] + i[6])
            xtimes[ind].append((i[1] - start) / 24 / 3600)
    total.append(total[-1])
    xtotal.append((end - start)/24/3600)
    ax = mainfig.add_subplot(111)
    ax.plot(xtotal, total, '^k-', lw=2, ms=5, label='Total')
    for i in range(len(accounts)):
        accs[i].append(accs[i][-1])
        xtimes[i].append((end - start)/24/3600)
        ax.plot(xtimes[i], accs[i], '+-', alpha=0.5, label=accounts[i])
    ax.plot([0, (end - start)/24/3600], [0, 0], '--r', alpha=0.3)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol=len(accounts) + 1)
    ax.set_xlabel('Time in days since the starting analysis date')
    ax.set_ylabel('Balance')
    ax.set_title('Time trends for the account balances')


def foo_weird(df_main, end, start, dates):
    pass

def graphical_analyze(event=None, but=None):
    mainfig.clear()
    titles = ['Categories', 'Payees', 'Accounts', 'Balance over time', 'Expenditure and Income over time']
    mainfig.suptitle(titles[but])
    df['Amount'] = df['Amount'].astype(float)
    dates = np.array([time.mktime(time.strptime(x, '%d/%m/%y')) for x in df['Date'].to_numpy()])
    try:  # validate date format
        start = time.mktime(time.strptime(date_start_2.get(), '%d/%m/%y'))
        end = time.mktime(time.strptime(date_end_2.get(), '%d/%m/%y'))
    except:
        val = status_graph_v.get()
        status_graph.config(text='Incorrect!', status=DISABLED)
        root.after(2000, lambda: status_graph.config(text=status_graph_v.set(val), status=NORMAL))
        return
    df_early = df.loc[dates < start, :]
    df_main = df.loc[np.logical_and(dates >= start, dates <= end), :].copy(deep=True)
    dates = np.array([time.mktime(time.strptime(x, '%d/%m/%y')) for x in df_main['Date'].to_numpy()])
    if but in [0, 1, 2]:
        foo_plot(['Category', 'Payee', 'Account'][but], df_main, end, start, dates)
    elif but == 3:
        foo_time(df_early, df_main, end, start, dates)
    elif but == 4:
        foo_weird(df_main, end, start, dates)
    mainfig.canvas.draw()


def focus_change(event=None):
    val = status_graph_v.get()
    txts = np.array(['Focus on Minus', 'Focus on Plus'])
    status_graph_v.set(txts[txts != val][0])
    status_graph.config(text=status_graph_v.get())


# GUI
root = Tk()
valid_entry = StringVar()
valid_entry.set('10')
nb = ttk.Notebook(root)

f1 = Frame(nb)

title1 = Label(f1, width=25, pady=5, font=('Helvetica', 25), text='New Transactions')
title1.grid(column=0, row=0, columnspan=6)
date1 = Entry(f1, width=13, bg='#d0f5c9', font=('Helvetica', 12))
date1.insert(0, time.strftime('%d/%m/%y', time.localtime()))
date1.bind('<FocusOut>', entryvalidate)
l_date1 = Label(f1, width=16, text='Date(dd/mm/yy)')
l_date1.grid(column=0, row=1)
date1.grid(column=0, row=2)

submit_button = ttk.Button(f1, text='Submit!')
submit_button.bind('<Button-1>', new_transaction)
submit_button.grid(column=6, row=0)

var_type = StringVar()
var_type.set('Minus')
var_type.trace('w', menu_alter)
type_m = OptionMenu(f1, var_type, *['Transfer', 'Minus', 'Plus'])
type_m['menu'].config(font=('Helvetica', 12))
type_m.grid(column=1, row=2)
l_type_m = Label(f1, width=10, text='Type')
l_type_m.grid(column=1, row=1)

var_from = StringVar()
var_from.set(accounts[0])
from_m = OptionMenu(f1, var_from, *accounts)
from_m['menu'].config(font=('Helvetica', 12))
from_m.grid(column=2, row=2)
l_from_m = Label(f1, width=10, text='From')
l_from_m.grid(column=2, row=1)

var_to = StringVar()
var_to.set(payees[0])
to_m = OptionMenu(f1, var_to, *payees)
to_m['menu'].config(font=('Helvetica', 12))
to_m.grid(column=3, row=2)
l_to_m = Label(f1, width=10, text='To')
l_to_m.grid(column=3, row=1)

var_category = StringVar()
var_category.set(categories[0])
category_m = OptionMenu(f1, var_category, *categories)
category_m['menu'].config(font=('Helvetica', 12))
category_m.grid(column=4, row=2)
l_category_m = Label(f1, width=10, text='Category')
l_category_m.grid(column=4, row=1)

amount = Entry(f1, width=13, bg='#f2b7b3', font=('Helvetica', 12))
amount.insert(0, '0')
amount.bind('<FocusOut>', entryvalidate2)
l_amount = Label(f1, width=16, text='Amount')
l_amount.grid(column=5, row=1)
amount.grid(column=5, row=2)

comments = Entry(f1, width=13, font=('Helvetica', 12))
l_comments = Label(f1, width=16, text='Comments')
l_comments.grid(column=6, row=1)
comments.grid(column=6, row=2)

title2 = Label(f1, width=25, pady=20, font=('Helvetica', 18), text='Payees')
title2.grid(column=0, row=3, columnspan=7)

new_payee = Entry(f1, width=25, font=('Helvetica', 12))
b_new_payee = ttk.Button(f1, text='Add New Payee')
b_new_payee.bind('<Button-1>', add_payee)
new_payee.grid(column=0, row=4, columnspan=2)
b_new_payee.grid(column=2, row=4)

del_sel = StringVar()
del_sel.set('')
del_payee = OptionMenu(f1, del_sel, *payees)
b_del_payee = ttk.Button(f1, text='Delete Payee')
b_del_payee.bind('<Button-1>', rem_payee)
del_payee.grid(column=4, row=4, columnspan=2)
b_del_payee.grid(column=6, row=4)

title3 = Label(f1, width=25, pady=20, font=('Helvetica', 18), text='Categories')
title3.grid(column=0, row=5, columnspan=7)

new_category = Entry(f1, width=25, font=('Helvetica', 12))
b_new_category = ttk.Button(f1, text='Add New Category')
b_new_category.bind('<Button-1>', add_category)
new_category.grid(column=0, row=6, columnspan=2)
b_new_category.grid(column=2, row=6)

del_sel_cat = StringVar()
del_sel_cat.set('')
del_category = OptionMenu(f1, del_sel_cat, *categories)
b_del_category = ttk.Button(f1, text='Delete Category')
b_del_category.bind('<Button-1>', rem_category)
del_category.grid(column=4, row=6, columnspan=2)
b_del_category.grid(column=6, row=6)

title4 = Label(f1, width=25, pady=20, font=('Helvetica', 18), text='Accounts')
title4.grid(column=0, row=7, columnspan=7)

new_account = Entry(f1, width=25, font=('Helvetica', 12))
b_new_account = ttk.Button(f1, text='Add New Account')
b_new_account.bind('<Button-1>', add_account)
new_account.grid(column=0, row=8, columnspan=2)
b_new_account.grid(column=2, row=8)

del_sel_acc = StringVar()
del_sel_acc.set('')
del_account = OptionMenu(f1, del_sel_acc, *accounts)
b_del_account = ttk.Button(f1, text='Delete Account')
b_del_account.bind('<Button-1>', rem_account)
del_account.grid(column=4, row=8, columnspan=2)
b_del_account.grid(column=6, row=8)

# root.protocol('WM_DELETE_WINDOW')
f2 = Frame(nb)
date_range_1 = Entry(f2, width=13, font=('Helvetica', 15), bg='#d0f5c9')
date_range_1.insert(0, time.strftime('%d/%m/%y', time.localtime(float(metadata[0]))))
date_range_1.bind('<FocusOut>', entryvalidate3)
date_range_2 = Entry(f2, width=13, font=('Helvetica', 15), bg='#d0f5c9')
date_range_2.insert(0, time.strftime('%d/%m/%y', time.localtime()))
date_range_2.bind('<FocusOut>', entryvalidate4)
date_range_l1 = Label(f2, text='From', font=('Helvetica', 15))
date_range_l2 = Label(f2, text='To', font=('Helvetica', 15))
date_range_l1.grid(row=0, column=0)
date_range_1.grid(column=1, row=0)
date_range_l2.grid(column=2, row=0)
date_range_2.grid(column=3, row=0)
f3 = Frame(f2)
list_account_s = Scrollbar(f3, orient=VERTICAL)
list_account = Listbox(f3, exportselection=0, selectmode=MULTIPLE, width=20, height=10, font=('Helvetica', 10),
                       yscrollcommand=list_account_s.set)
for i in accounts:
    list_account.insert(END, i)
list_account_s.config(command=list_account.yview)
list_account.selection_set(0, END)

list_payee_s = Scrollbar(f3, orient=VERTICAL)
list_payee = Listbox(f3, exportselection=0, selectmode=MULTIPLE, width=20, height=10, font=('Helvetica', 10),
                     yscrollcommand=list_payee_s.set)
for i in payees:
    list_payee.insert(END, i)
list_payee_s.config(command=list_payee.yview)
list_payee.selection_set(0, END)

list_category_s = Scrollbar(f3, orient=VERTICAL)
list_category = Listbox(f3, exportselection=0, selectmode=MULTIPLE, width=20, height=10, font=('Helvetica', 10),
                        yscrollcommand=list_category_s.set)
for i in categories:
    list_category.insert(END, i)
list_category_s.config(command=list_category.yview)
list_category.selection_set(0, END)

list_type_s = Scrollbar(f3, orient=VERTICAL)
list_type = Listbox(f3, exportselection=0, selectmode=MULTIPLE, width=20, height=10, font=('Helvetica', 10),
                    yscrollcommand=list_type_s.set)
for i in ['Transfer', 'Minus', 'Plus']:
    list_type.insert(END, i)
list_type_s.config(command=list_type.yview)
list_type.selection_set(0, END)

list_type.pack(side=LEFT)
list_type_s.pack(side=LEFT, fill=Y)
list_account.pack(side=LEFT)
list_account_s.pack(side=LEFT, fill=Y)
list_category.pack(side=LEFT, fill=Y)
list_category_s.pack(side=LEFT, fill=Y)
list_payee.pack(side=LEFT)
list_payee_s.pack(side=LEFT, fill=Y)
f3.grid(column=4, row=0)

refresh = ttk.Button(f2, text='Refresh')
refresh.bind('<Button-1>', view_refresh)
refresh.grid(column=5, row=0)
viewmain = scrolledtext.ScrolledText(f2, font=('Lucida Console', 10), height=30, width=150, wrap=NONE)
viewmain.grid(column=0, row=1, columnspan=6)

f4 = Frame(nb)
date_start = Entry(f4, width=13, font=('Helvetica', 15), bg='#d0f5c9')
date_start.insert(0, time.strftime('%d/%m/%y', time.localtime(float(metadata[0]))))
date_end = Entry(f4, width=13, font=('Helvetica', 15), bg='#d0f5c9')
date_end.insert(0, time.strftime('%d/%m/%y', time.localtime()))
date_start_l = Label(f4, text='Analysis from ', font=('Helvetica', 15))
date_end_l = Label(f4, text='to', font=('Helvetica', 15))
date_start_l.grid(column=2, row=0)
date_start.grid(column=3, row=0)
date_end_l.grid(column=4, row=0)
date_end.grid(column=5, row=0)
analyze = ttk.Button(f4, text='Analyze!')
analyze.bind('<Button-1>', numeric_analyze)
analyze.grid(column=7, row=0)

Label(f4, text='Account', height=1, width=18, font=('Lucida Console', 10)).grid(column=0, row=1)
Label(f4, text='Opening Balance', height=1, width=18, font=('Lucida Console', 10)).grid(column=1, row=1)
Label(f4, text='Total Entries', height=1, width=18, font=('Lucida Console', 10)).grid(column=2, row=1)
Label(f4, text='Closing Balance', height=1, width=18, font=('Lucida Console', 10)).grid(column=3, row=1)
Label(f4, text='Difference', height=1, width=18, font=('Lucida Console', 10)).grid(column=4, row=1)
Label(f4, text='Max Payee Minus', height=1, width=18, font=('Lucida Console', 10)).grid(column=5, row=1)
Label(f4, text='Max Payee Plus', height=1, width=18, font=('Lucida Console', 10)).grid(column=6, row=1)
Label(f4, text='Most Category', height=1, width=18, font=('Lucida Console', 10)).grid(column=7, row=1)
Label(f4, text=''.join(['_'] * (18 * 8)), font=('Lucida Console', 10)).grid(row=2, column=0, columnspan=8)
major_label_1 = Label(f4, width=18, text='', font=('Lucida Console', 10))
major_label_2 = Label(f4, width=18, text='', font=('Lucida Console', 10))
major_label_3 = Label(f4, width=18, text='', font=('Lucida Console', 10))
major_label_4 = Label(f4, width=18, text='', font=('Lucida Console', 10))
major_label_5 = Label(f4, width=18, text='', font=('Lucida Console', 10))
major_label_6 = Label(f4, width=18, text='', font=('Lucida Console', 10))
major_label_7 = Label(f4, width=18, text='', font=('Lucida Console', 10))
major_label_8 = Label(f4, width=18, text='', font=('Lucida Console', 10))
major_label_1.grid(column=0, row=3)
major_label_2.grid(column=1, row=3)
major_label_3.grid(column=2, row=3)
major_label_4.grid(column=3, row=3)
major_label_5.grid(column=4, row=3)
major_label_6.grid(column=5, row=3)
major_label_7.grid(column=6, row=3)
major_label_8.grid(column=7, row=3)
Label(f4, text=''.join(['_'] * (18 * 8)), font=('Lucida Console', 10)).grid(row=4, column=0, columnspan=8)
total_label_1 = Label(f4, width=18, text='Total', font=('Lucida Console', 10))
total_label_2 = Label(f4, width=18, text='', font=('Lucida Console', 10))
total_label_3 = Label(f4, width=18, text='', font=('Lucida Console', 10))
total_label_4 = Label(f4, width=18, text='', font=('Lucida Console', 10))
total_label_5 = Label(f4, width=18, text='', font=('Lucida Console', 10))
total_label_6 = Label(f4, width=18, text='', font=('Lucida Console', 10))
total_label_7 = Label(f4, width=18, text='', font=('Lucida Console', 10))
total_label_8 = Label(f4, text='', width=18, font=('Lucida Console', 10))
total_label_1.grid(column=0, row=5)
total_label_2.grid(column=1, row=5)
total_label_3.grid(column=2, row=5)
total_label_4.grid(column=3, row=5)
total_label_5.grid(column=4, row=5)
total_label_6.grid(column=5, row=5)
total_label_7.grid(column=6, row=5)
total_label_8.grid(column=7, row=5)
payee_numeric = scrolledtext.ScrolledText(f4, width=18 * 4, height=15)
category_numeric = scrolledtext.ScrolledText(f4, width=18 * 4, height=15)
payee_numeric.grid(row=6, column=0, columnspan=4)
category_numeric.grid(row=6, column=4, columnspan=4)
numeric_analyze()

f5 = Frame(nb)
date_start_2 = Entry(f5, width=13, font=('Helvetica', 15), bg='#d0f5c9')
date_start_2.insert(0, time.strftime('%d/%m/%y', time.localtime(float(metadata[0]))))
date_end_2 = Entry(f5, width=13, font=('Helvetica', 15), bg='#d0f5c9')
date_end_2.insert(0, time.strftime('%d/%m/%y', time.localtime()))
date_start_2_l = Label(f5, text='Analysis from ', font=('Helvetica', 15))
date_end_2_l = Label(f5, text='to', font=('Helvetica', 15))
date_start_2_l.grid(column=0, row=0)
date_start_2.grid(column=1, row=0)
date_end_2_l.grid(column=2, row=0)
date_end_2.grid(column=3, row=0)
status_graph_v = StringVar()
status_graph_v.set('Focus on Minus')
status_graph = ttk.Button(f5, text='Focus on Minus')
status_graph.grid(row=0, column=4)
status_graph.bind('<Button-1>', focus_change)
mainfig = Figure(figsize=(12, 7), dpi=100)
maincanvas = FigureCanvasTkAgg(mainfig, f5)
maincanvas.get_tk_widget().grid(row=2, column=0, columnspan=5)
load_buttons = []
for i in range(5):
    load_buttons.append(ttk.Button(f5, text='Graph ' + str(i + 1)))
    load_buttons[-1].bind('<Button-1>', lambda x, y=i: graphical_analyze(x, y))
    load_buttons[-1].grid(row=1, column=i)
graphical_analyze(but=0)

nb.add(f1, text='Entry form')
nb.add(f2, text='View')
nb.add(f4, text='Numeric')
nb.add(f5, text='Graphical')

nb.pack()
root.mainloop()

if input('Save (y/n): ').lower() == 'y':
    encrypt_db(dbpath, p, metadata[0], df, t_count, categories, accounts, payees)
    quit(0)
